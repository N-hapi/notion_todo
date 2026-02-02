"""Services for Notion Todo integration."""
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.service import async_register_admin_service

from .const import DOMAIN
from .coordinator import NotionDataUpdateCoordinator


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up Notion Todo services."""

    async def create_task_service(call: ServiceCall) -> None:
        """Create a new task in Notion."""
        task_name = call.data.get("task_name")
        # Default to "Household" if not provided
        project = call.data.get("omnifocus_project", "Household")

        # Format select field for Notion API
        project_select = {"select": {"name": project}}

        # Get the first coordinator (if multiple entries, use the first one)
        entries = hass.data[DOMAIN]
        if not entries:
            return

        coordinator: NotionDataUpdateCoordinator = next(iter(entries.values()))

        # Create the task
        await coordinator.client.create_task(
            title=task_name,
            status="not-started",
            omnifocus_project=project_select
        )

        # Refresh data
        await coordinator.async_refresh()

    async_register_admin_service(
        hass,
        DOMAIN,
        "create_task",
        create_task_service,
        schema={
            "type": "object",
            "properties": {
                "task_name": {
                    "type": "string",
                    "description": "Name of the task to create",
                },
                "omnifocus_project": {
                    "type": "string",
                    "description": "OmniFocus project (defaults to Household)",
                },
            },
            "required": ["task_name"],
        },
    )