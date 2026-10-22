# Venture mobile app

## Online and offline behaviour

When connected, the app requests weather and forecasts from the backend and saves
successful responses on the device. If a later request fails because of a
connection problem or server error, it uses the saved response for the same
trail and date selection. Weather and forecast screens identify saved responses
as offline copies and show when they were last received. Treat saved information
as potentially outdated; it is not a replacement for current official guidance.

The cache is specific to each trail/date (and forecast date range), so changing
the selection while offline may not have a saved response. The interactive
OpenStreetMap background still needs an internet connection; offline map-tile
downloads are not implemented.

To demonstrate offline behaviour, first load a trail's weather and forecast
while online, then disable the network and request the same trail and dates
again. The app should show the saved values and an offline warning.
