var activeWindow = null;

function sendLog(window) {
    var appClass = window ? (window.resourceClass || "Unknown") : "Desktop";
    var title = window ? (window.caption || "Unknown") : "Desktop";

    callDBus(
        "kwin.windowtracker",
        "/Logger",
        "kwin.windowtracker",
        "Log",
        appClass,
        title
    );
}

function onCaptionChanged() {
    // Whenever the active window changes its title (like switching tabs)
    if (activeWindow) {
        sendLog(activeWindow);
    }
}

workspace.windowActivated.connect(function(window) {
    // 1. Disconnect the title listener from the OLD window so it stops logging in the background
    if (activeWindow && activeWindow.captionChanged) {
        try {
            activeWindow.captionChanged.disconnect(onCaptionChanged);
        } catch(e) {
            // Ignore if it wasn't connected
        }
    }

    // 2. Update our tracker to the newly focused window
    activeWindow = window;

    // 3. Connect the title listener to the NEW window
    if (activeWindow && activeWindow.captionChanged) {
        activeWindow.captionChanged.connect(onCaptionChanged);
    }

    // 4. Log the initial window switch
    sendLog(activeWindow);
});
