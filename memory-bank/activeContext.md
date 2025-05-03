# ConsultEase - Active Context

## Current Focus
Continuing to stabilize and refine the core application, particularly focusing on UI consistency, hardware interaction (RFID), and fixing runtime issues identified during testing on the Raspberry Pi. Ensured the application starts correctly and core navigation (logout, fullscreen toggle) works as expected.

## Recent Changes
- Fixed application startup issues related to duplicate `QApplication` instances and incorrect method calls.
- Enabled RFID simulation mode by default in the main application script for easier testing/deployment.
- Corrected `AttributeError` caused by attempting `setWindowState` on `QApplication`.
- Fixed `AttributeError` related to incorrect icon loading (`icons.get_icon` vs `IconProvider.get_icon`).
- Resolved UI inconsistencies in the Login screen:
    - Removed unnecessary blue side panel.
    - Correctly positioned the "Simulate RFID Scan" button within the scanning frame.
    - Re-implemented manual RFID input field and submit button.
- Addressed RFID scanning/capture issues in the Admin Dashboard (Student Management):
    - Improved callback handling in `RFIDScanDialog` to prevent missed scans.
    - Added manual input fallback to `RFIDScanDialog`.
    - Enhanced `RFIDService` to better handle 13.56 MHz card characteristics (expanded key map, longer simulated UID).
    - Corrected logic in `RFIDService` to perform student lookup *before* notifying callbacks, ensuring the correct student object is passed.
- Fixed Admin Dashboard logout functionality to correctly emit `change_window` signal and return to the admin login screen.
- Implemented F11 key shortcut in `BaseWindow` to allow toggling fullscreen mode.

## Next Steps
- Verify RFID scanning reliability on the login screen with the recent service-level fixes.
- Conduct further testing on the Raspberry Pi hardware, especially with the actual 13.56 MHz RFID reader if available.
- Address any remaining UI/UX inconsistencies or bugs reported.
- Potentially revisit BLE beacon handling if issues arise during integration testing.
- Begin integration testing phase with all hardware components (Raspberry Pi, ESP32 Desk Unit, RFID Reader).

## Active Decisions and Considerations
- **UI Design Pattern**: Using PyQt5 with a modular design pattern separating models, views, and controllers (MVC).
- **UI Theme**: Currently using a dark theme inherited from the initial setup, but previous context mentioned a switch to light (white/navy/gold). *Verify intended theme.*
- **Database Access**: Using SQLAlchemy ORM for database operations.
- **Inter-device Communication**: Using MQTT as the backbone for communication between Central System and Faculty Desk Units.
- **Authentication Flow**: Two separate authentication paths - RFID for students and username/password for admins. Student RFID lookup now happens earlier in the `RFIDService`.
- **Thread Safety**: Using Qt's signal-slot mechanism to ensure thread-safe UI updates. Callback management in RFID dialogs improved.
- **Deployment Strategy**: Developing automated setup scripts for the Raspberry Pi. Fullscreen toggle (F11) added.
- **Admin Interface**: Comprehensive dashboard with tabs for managing faculty, students, and system maintenance. RFID scanning workflow refined.
- **Touch Optimization**: Enhanced UI elements with larger touch targets and optimized spacing.
- **Keyboard Integration**: Auto-showing virtual keyboard for text input fields (squeekboard).

## Learnings and Project Insights
- Callback management in asynchronous operations (like RFID reading across different dialogs) requires careful handling to prevent garbage collection and ensure proper registration/unregistration.
- Hardware interaction (RFID) often requires specific character mapping and handling based on the reader and card type (e.g., 13.56 MHz). Providing manual input fallbacks is crucial.
- Debugging PyQt application startup requires checking `QApplication` instantiation and main loop execution (`app.run()`).
- Thoroughly testing UI interactions (like logout, fullscreen toggle) across different application states is important.
- Framework specifics matter (e.g., `setWindowState` is for `QMainWindow`, not `QApplication`). Icon loading requires using the correct provider class (`IconProvider`).

## Important Patterns and Preferences

### Code Organization
- Python code follows PEP 8 style guide.
- Modular architecture with clear separation of concerns (models, views, controllers, services, utils).

### UI Patterns
- Consistent styling applied via `BaseWindow` and stylesheets.
- Fullscreen toggle via F11 key.
- Manual input fallback provided for hardware-dependent features (RFID scan).
- Status indicators use consistent color coding.
- Confirmations required for destructive actions.
- Auto-appearing on-screen keyboard for text input.

### Naming Conventions
- CamelCase for class names.
- snake_case for variables and function names.
- UPPERCASE for constants.
- Descriptive names that reflect purpose 