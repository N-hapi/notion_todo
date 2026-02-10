"""Services for Notion Todo integration."""
from datetime import datetime
import logging
from homeassistant.core import HomeAssistant, ServiceCall
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN
from .coordinator import NotionDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up Notion Todo services."""
    
    # Only register services once
    if hass.services.has_service(DOMAIN, "create_task"):
        return

    async def create_task_service(call: ServiceCall) -> None:
        """Create a new task in Notion."""
        task_name = call.data.get("task_name")
        project = call.data.get("omnifocus_project", "Household")
        due_date_str = call.data.get("due_date")
        
        # Parse due date if provided
        due_date = None
        if due_date_str:
            if due_date_str == "today":
                # Format as ISO date string (YYYY-MM-DD)
                due_date = datetime.now().date().isoformat()
            else:
                try:
                    # Parse and convert to ISO format
                    parsed_date = datetime.fromisoformat(due_date_str)
                    due_date = parsed_date.date().isoformat()
                except ValueError:
                    try:
                        # Try parsing as date only
                        parsed_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                        due_date = parsed_date.date().isoformat()
                    except ValueError:
                        # If all parsing fails, log error and skip date
                        _LOGGER.error("Invalid date format: %s", due_date_str)
                        due_date = None

        # Get the first coordinator
        entries = hass.data[DOMAIN]
        if not entries:
            return

        coordinator: NotionDataUpdateCoordinator = next(iter(entries.values()))

        # Create the task with correct status format
        await coordinator.client.create_task(
            title=task_name,
            status="Not_started",
            omnifocus_project=project,
            due=due_date  # Now passing ISO date string
        )

        # Refresh data
        await coordinator.async_refresh()

    hass.services.async_register(
        DOMAIN,
        "create_task",
        create_task_service,
        schema=vol.Schema({
            vol.Required("task_name"): cv.string,
            vol.Optional("omnifocus_project", default="Household"): cv.string,
            vol.Optional("due_date"): cv.string,  # Accepts "today", "YYYY-MM-DD", or ISO format
        }),
    )