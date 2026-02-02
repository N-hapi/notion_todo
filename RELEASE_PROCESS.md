# Release Process

Follow these steps to create a new release for the Notion ToDo integration.

## Step 1: Make and Test Code Changes

Make your changes to the codebase and test them locally to ensure everything works correctly.

## Step 2: Update Version in Manifest

Update the version number in `custom_components/notion_todo/manifest.json`:

```json
"version": "0.0.4"  // bump from previous version
```

Use semantic versioning (e.g., 0.0.1 → 0.0.2 → 0.0.3, or 0.1.0 for minor changes).

## Step 3: Commit and Push to GitHub

```bash
cd /Users/naelalshowaikh/Downloads/notion_todo-main
git add custom_components/notion_todo/manifest.json
git commit -m "Bump version to 0.0.4"
git push origin main
```

## Step 4: Create the Release Zip File

**IMPORTANT:** Run this command from the `custom_components/` directory to ensure correct folder structure.

```bash
cd /Users/naelalshowaikh/Downloads/notion_todo-main/custom_components
rm -f ../notion_todo.zip
zip -r ../notion_todo.zip notion_todo
```

This creates a zip with the correct structure:
```
notion_todo/
├── __init__.py
├── manifest.json
├── config_flow.py
├── coordinator.py
├── api.py
├── const.py
├── todo.py
├── notion_property_helper.py
├── requirements.txt
└── translations/
    ├── en.json
    └── de.json
```

## Step 5: Create GitHub Release

1. Go to: https://github.com/N-hapi/notion_todo/releases/new
2. **Tag version:** Enter `0.0.4` (must match manifest.json version)
3. **Release title:** `Version 0.0.4`
4. **Description:** Add your release notes describing changes
5. **Attach the zip file:** Upload `notion_todo.zip` from step 4
6. Click **"Publish release"**

## Step 6: Users Install the Integration

Users will:
1. Download the zip from the GitHub release
2. Extract it to their Home Assistant `custom_components/` folder
3. Restart Home Assistant
4. Go to Settings → Devices & Services
5. Search for "Notion" or "notion_todo"
6. Add the integration and enter their API credentials

## Common Issues

### Integration doesn't show up after installation
- **Restart Home Assistant** - Always required after adding a custom integration
- **Check folder structure** - Must be `custom_components/notion_todo/manifest.json` (not double-nested)
- **Check Home Assistant logs** - Settings → System → Logs for errors

### Zip structure is wrong
- **Always run `zip -r`** from the `custom_components/` directory
- Do NOT zip from the root directory or you'll get extra folder levels

### Version mismatch error
- The tag in GitHub release must exactly match the version in `manifest.json`
