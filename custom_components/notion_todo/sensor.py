"""A sensor platform for Notion tasks properties."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    TASK_COMPLETED_PROPERTY,
    TASK_FROG_PROPERTY,
    TASK_WEEKEND_PROPERTY,
    TASK_10MIN_PROPERTY,
    TASK_PROJECT_PROPERTY,
)
from .coordinator import NotionDataUpdateCoordinator
from .notion_property_helper import NotionPropertyHelper as propHelper


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the sensor platform config entry."""
    coordinator: NotionDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities(
        [
            NotionTasksWithFrogSensor(coordinator),
            NotionTasksWithWeekendSensor(coordinator),
            NotionTasksQuick10MinSensor(coordinator),
            NotionTasksCompletedSensor(coordinator),
            NotionTasksByProjectSensor(coordinator),
        ]
    )


class NotionTasksWithFrogSensor(CoordinatorEntity[NotionDataUpdateCoordinator], SensorEntity):
    """Sensor for tasks marked with Frog."""

    _attr_name = "Notion Tasks with Frog"
    _attr_unique_id = "notion_tasks_frog"
    _attr_native_unit_of_measurement = "tasks"

    def __init__(self, coordinator: NotionDataUpdateCoordinator) -> None:
        """Initialize sensor."""
        super().__init__(coordinator=coordinator)
        self._attr_unique_id = f"notion_frog_{coordinator.config_entry.entry_id}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data is None:
            self._attr_native_value = 0
        else:
            frog_tasks = []
            for task in self.coordinator.data['results']:
                frog_value = propHelper.get_property_by_id(TASK_FROG_PROPERTY, task)
                if frog_value:
                    task_name = propHelper.get_property_by_id('title', task)
                    frog_tasks.append(f"{task_name} ({frog_value})")
            
            self._attr_native_value = len(frog_tasks)
            self._attr_extra_state_attributes = {
                "tasks": frog_tasks,
            }
        super()._handle_coordinator_update()


class NotionTasksWithWeekendSensor(CoordinatorEntity[NotionDataUpdateCoordinator], SensorEntity):
    """Sensor for weekend tasks."""

    _attr_name = "Notion Weekend Tasks"
    _attr_unique_id = "notion_tasks_weekend"
    _attr_native_unit_of_measurement = "tasks"

    def __init__(self, coordinator: NotionDataUpdateCoordinator) -> None:
        """Initialize sensor."""
        super().__init__(coordinator=coordinator)
        self._attr_unique_id = f"notion_weekend_{coordinator.config_entry.entry_id}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data is None:
            self._attr_native_value = 0
        else:
            weekend_tasks = []
            for task in self.coordinator.data['results']:
                weekend_value = propHelper.get_property_by_id(TASK_WEEKEND_PROPERTY, task)
                if weekend_value:  # True if checkbox is checked
                    task_name = propHelper.get_property_by_id('title', task)
                    weekend_tasks.append(task_name)
            
            self._attr_native_value = len(weekend_tasks)
            self._attr_extra_state_attributes = {
                "tasks": weekend_tasks,
            }
        super()._handle_coordinator_update()


class NotionTasksQuick10MinSensor(CoordinatorEntity[NotionDataUpdateCoordinator], SensorEntity):
    """Sensor for quick <10min tasks."""

    _attr_name = "Notion Quick 10min Tasks"
    _attr_unique_id = "notion_tasks_quick"
    _attr_native_unit_of_measurement = "tasks"

    def __init__(self, coordinator: NotionDataUpdateCoordinator) -> None:
        """Initialize sensor."""
        super().__init__(coordinator=coordinator)
        self._attr_unique_id = f"notion_quick_{coordinator.config_entry.entry_id}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data is None:
            self._attr_native_value = 0
        else:
            quick_tasks = []
            for task in self.coordinator.data['results']:
                quick_value = propHelper.get_property_by_id(TASK_10MIN_PROPERTY, task)
                if quick_value:  # True if checkbox is checked
                    task_name = propHelper.get_property_by_id('title', task)
                    quick_tasks.append(task_name)
            
            self._attr_native_value = len(quick_tasks)
            self._attr_extra_state_attributes = {
                "tasks": quick_tasks,
            }
        super()._handle_coordinator_update()


class NotionTasksCompletedSensor(CoordinatorEntity[NotionDataUpdateCoordinator], SensorEntity):
    """Sensor for completed tasks."""

    _attr_name = "Notion Completed Tasks"
    _attr_unique_id = "notion_tasks_completed"
    _attr_native_unit_of_measurement = "tasks"

    def __init__(self, coordinator: NotionDataUpdateCoordinator) -> None:
        """Initialize sensor."""
        super().__init__(coordinator=coordinator)
        self._attr_unique_id = f"notion_completed_{coordinator.config_entry.entry_id}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data is None:
            self._attr_native_value = 0
        else:
            completed_tasks = []
            for task in self.coordinator.data['results']:
                completed_value = propHelper.get_property_by_id(TASK_COMPLETED_PROPERTY, task)
                if completed_value:  # True if checkbox is checked
                    task_name = propHelper.get_property_by_id('title', task)
                    completed_tasks.append(task_name)
            
            self._attr_native_value = len(completed_tasks)
            self._attr_extra_state_attributes = {
                "tasks": completed_tasks,
            }
        super()._handle_coordinator_update()


class NotionTasksByProjectSensor(CoordinatorEntity[NotionDataUpdateCoordinator], SensorEntity):
    """Sensor for tasks grouped by project."""

    _attr_name = "Notion Tasks by Project"
    _attr_unique_id = "notion_tasks_by_project"

    def __init__(self, coordinator: NotionDataUpdateCoordinator) -> None:
        """Initialize sensor."""
        super().__init__(coordinator=coordinator)
        self._attr_unique_id = f"notion_by_project_{coordinator.config_entry.entry_id}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data is None:
            self._attr_native_value = 0
        else:
                projects_dict = {}
                for task in self.coordinator.data['results']:
                    project_property = propHelper.get_property_by_id(TASK_PROJECT_PROPERTY, task)
                    task_name = propHelper.get_property_by_id('title', task)
                    if task_name:
                        task_name = task_name.strip()
                    project_names = []
                    # Extract project names from the select field
                    if project_property and isinstance(project_property, dict):
                        select_field = project_property.get('select')
                        if select_field and isinstance(select_field, dict):
                            options = select_field.get('options')
                            if options and isinstance(options, list):
                                for option in options:
                                    name = option.get('name')
                                    if name:
                                        project_names.append(name)
                    if project_names:
                        for project_name in project_names:
                            if project_name not in projects_dict:
                                projects_dict[project_name] = []
                            projects_dict[project_name].append(task_name)
                    else:
                        if "No Project" not in projects_dict:
                            projects_dict["No Project"] = []
                        projects_dict["No Project"].append(task_name)
                self._attr_native_value = len(projects_dict)
                self._attr_extra_state_attributes = {
                    "projects": projects_dict,
                }
        super()._handle_coordinator_update()
