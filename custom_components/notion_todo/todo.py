"""A todo platform for Notion."""

import asyncio
from typing import cast

from homeassistant.components.todo import (
    TodoItem,
    TodoItemStatus,
    TodoListEntity,
    TodoListEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    TASK_STATUS_PROPERTY,
    TASK_DATE_PROPERTY,
    TASK_FROG_PROPERTY,
    TASK_WEEKEND_PROPERTY,
    TASK_10MIN_PROPERTY,
    TASK_COMPLETED_PROPERTY,
    TASK_PROJECT_PROPERTY,
)
from .coordinator import NotionDataUpdateCoordinator
from .notion_property_helper import NotionPropertyHelper as propHelper

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the todo platform config entry."""
    coordinator: NotionDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        NotionTodoListEntity(coordinator, 'Notion', None),
        NotionTodoListEntity(coordinator, 'Notion Frog Tasks', TASK_FROG_PROPERTY),
        NotionTodoListEntity(coordinator, 'Notion Weekend Tasks', TASK_WEEKEND_PROPERTY),
        NotionTodoListEntity(coordinator, 'Notion Quick 10min Tasks', TASK_10MIN_PROPERTY),
        NotionTodoListEntity(coordinator, 'Notion Completed Tasks', TASK_COMPLETED_PROPERTY),
    ]
    
    async_add_entities(entities)

STATUS_IN_PROGRESS = 'In_progress'
STATUS_ARCHIVED = 'Paused'
STATUS_DONE = 'Done'
STATUS_NOT_STARTED = 'Not_started'
NOTION_TO_HASS_STATUS = {
    STATUS_NOT_STARTED: TodoItemStatus.NEEDS_ACTION,
    STATUS_IN_PROGRESS: TodoItemStatus.NEEDS_ACTION,
    STATUS_DONE: TodoItemStatus.COMPLETED,
    STATUS_ARCHIVED: TodoItemStatus.COMPLETED
}
HASS_TO_NOTION_STATUS = {
    TodoItemStatus.NEEDS_ACTION: STATUS_NOT_STARTED,
    TodoItemStatus.COMPLETED: STATUS_DONE
}

class NotionTodoListEntity(CoordinatorEntity[NotionDataUpdateCoordinator], TodoListEntity):
    """A Notion TodoListEntity."""

    _attr_supported_features = (
        TodoListEntityFeature.CREATE_TODO_ITEM
        | TodoListEntityFeature.UPDATE_TODO_ITEM
        | TodoListEntityFeature.DELETE_TODO_ITEM
        | TodoListEntityFeature.SET_DESCRIPTION_ON_ITEM
        | TodoListEntityFeature.SET_DUE_DATE_ON_ITEM
        | TodoListEntityFeature.SET_DUE_DATETIME_ON_ITEM
    )

    def __init__(
        self,
        coordinator: NotionDataUpdateCoordinator,
        name: str,
        filter_property: str | None = None,
    ) -> None:
        """Initialize TodoListEntity."""
        super().__init__(coordinator=coordinator)
        self._filter_property = filter_property
        self._attr_unique_id = f"{name.lower().replace(' ', '_')}_{coordinator.config_entry.entry_id}"
        self._attr_name = name
        self._status = {}

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data is None:
            self._attr_todo_items = None
        else:
            items = []
            for task in self.coordinator.data['results']:
                # Apply filter if specified
                if self._filter_property is not None:
                    filter_value = propHelper.get_property_by_id(self._filter_property, task)
                    if not filter_value:  # Skip if filter property is False or None
                        continue
                
                id = task['id']
                status_value = propHelper.get_property_by_id(TASK_STATUS_PROPERTY, task)
                self._status[id] = status_value
                
                # Default to NEEDS_ACTION if status not found or unknown
                status = NOTION_TO_HASS_STATUS.get(status_value, TodoItemStatus.NEEDS_ACTION)
                
                # Get all properties
                title = propHelper.get_property_by_id('title', task)
                due_date = propHelper.get_property_by_id(TASK_DATE_PROPERTY, task)
                frog_value = propHelper.get_property_by_id(TASK_FROG_PROPERTY, task)
                weekend_value = propHelper.get_property_by_id(TASK_WEEKEND_PROPERTY, task)
                quick_value = propHelper.get_property_by_id(TASK_10MIN_PROPERTY, task)
                completed_value = propHelper.get_property_by_id(TASK_COMPLETED_PROPERTY, task)
                project_value = propHelper.get_property_by_id(TASK_PROJECT_PROPERTY, task)
                
                # Build description with all attributes
                description_parts = []
                if project_value:
                    description_parts.append(f"Project: {project_value}")
                if frog_value:
                    description_parts.append(f"Frog: {frog_value}")
                if weekend_value:
                    description_parts.append("Weekend task")
                if quick_value:
                    description_parts.append("Quick <10min")
                if completed_value:
                    description_parts.append("Completed ✓")
                
                description = " | ".join(description_parts) if description_parts else None

                items.append(
                    TodoItem(
                        summary=title,
                        uid=id,
                        status=status,
                        description=description,
                        due=due_date
                    )
                )
            self._attr_todo_items = items
        super()._handle_coordinator_update()

    async def async_create_todo_item(self, item: TodoItem) -> None:
        """Create a To-do item."""
        await self.coordinator.client.create_task(item.summary, status=HASS_TO_NOTION_STATUS[item.status])
        await self.coordinator.async_refresh()

    async def async_update_todo_item(self, item: TodoItem) -> None:
        """Update a To-do item."""
        uid: str = cast(str, item.uid)
        status = HASS_TO_NOTION_STATUS[item.status]
        if self._status[uid] == STATUS_IN_PROGRESS and status == STATUS_NOT_STARTED:
            status = STATUS_IN_PROGRESS
        if self._status[uid] == STATUS_ARCHIVED and status == STATUS_DONE:
            status = STATUS_ARCHIVED

        await self.coordinator.client.update_task(task_id=uid,
                                                  title=item.summary,
                                                  status=status,
                                                  due=item.due,
                                                  description=item.description)

        await self.coordinator.async_refresh()

    async def async_delete_todo_items(self, uids: list[str]) -> None:
        """Delete a To-do item."""
        await asyncio.gather(
            *[self.coordinator.client.delete_task(task_id=uid) for uid in uids]
        )
        await self.coordinator.async_refresh()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass update state from existing coordinator data."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()