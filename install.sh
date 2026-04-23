#!/bin/bash
docker cp custom_components/notion_todo homeassistant:/config/custom_components/
docker restart homeassistant
