# ConsultEase - Active Context

## Current Focus
We have completed the initial development of the ConsultEase system, including the core UI components, database integration, and faculty desk unit functionality. We are now focusing on optimizing the system for the Raspberry Pi touchscreen environment with enhanced touch-friendly UI and on-screen keyboard integration. The latest update includes a UI theme refresh with a clean white background and navy blue/gold accent colors.

## Recent Changes
- Created database models for Faculty, Student, Consultation, and Admin
- Implemented MQTT and RFID services
- Developed PyQt UI components (Login, Dashboard, Admin Login)
- Created controller classes to manage application logic
- Developed Faculty Desk Unit firmware with BLE presence detection
- Created BLE beacon firmware for faculty members
- Added comprehensive documentation and deployment guides
- Enhanced user manual with a Quick Start Guide, BLE Beacon Maintenance, and Technical Appendix
- Implemented Admin Dashboard with Faculty Management, Student Management, and System Maintenance tabs
- Added on-screen keyboard integration with automatic popup/hide behaviors
- Optimized UI elements for touch interaction with larger buttons and touch-friendly spacing
- Created installation scripts for touchscreen dependencies
- Updated UI theme to use a white background with navy blue (#0d3b66) and gold (#ffc233) accent colors for improved aesthetics and readability

## Next Steps
- Implement fullscreen mode for touchscreen deployment
- Enhance touch calibration support
- Conduct integration testing with real hardware
- Develop training materials for system users
- Implement security hardening (TLS for MQTT, secure password storage)
- Optimize power management for BLE beacons

## Active Decisions and Considerations
- **UI Design Pattern**: Using PyQt5 with a modular design pattern separating models, views, and controllers (MVC)
- **UI Theme**: White background with navy blue (#0d3b66) and gold (#ffc233) accents for a clean, professional appearance
- **Database Access**: Using SQLAlchemy ORM for database operations
- **Inter-device Communication**: Using MQTT as the backbone for communication between Central System and Faculty Desk Units
- **Authentication Flow**: Two separate authentication paths - RFID for students and username/password for admins
- **Thread Safety**: Using Qt's signal-slot mechanism to ensure thread-safe UI updates
- **Deployment Strategy**: Developing automated setup scripts for the Raspberry Pi
- **Admin Interface**: Comprehensive dashboard with tabs for managing faculty, students, and system maintenance
- **Touch Optimization**: Enhanced UI elements with larger touch targets and optimized spacing
- **Keyboard Integration**: Auto-showing virtual keyboard for text input fields

## Learnings and Project Insights
- RFID integration with Python on Raspberry Pi requires proper threading and event handling
- BLE RSSI values can fluctuate significantly; filtering/thresholding is necessary for accurate presence detection
- MQTT with QoS 1 provides a good balance between reliability and performance for this application
- SQLAlchemy ORM simplifies database operations while providing flexibility
- PyQt's MVC pattern facilitates code organization but requires careful signal/slot connections
- System maintenance functionality (database backup/restore, log viewing) is essential for admin operations
- On-screen keyboard integration is crucial for touchscreen deployments
- Different Linux distributions may have different virtual keyboards available (squeekboard, onboard, matchbox-keyboard)
- Touch-optimized UI requires larger targets and clear visual feedback
- UI color schemes should prioritize contrast and readability while maintaining professional appearance

## Important Patterns and Preferences

### Code Organization
- Python code follows PEP 8 style guide
- C++ code for ESP32 follows Arduino style guidelines
- Modular architecture with clear separation of concerns
- Configuration values stored in separate config files

### UI Patterns
- Consistent color scheme across all screens (white background, navy blue and gold accents)
- Primary buttons use gold (#ffc233) with navy text for emphasis
- Standard buttons and interactive elements use navy blue (#0d3b66)
- Touch-friendly large buttons and elements
- Status indicators use consistent color coding (green=available, red=unavailable)
- Confirmations required for destructive actions
- Auto-appearing on-screen keyboard for text input
- Minimum touch target size of 48x48 pixels (converted to appropriate units)

### Naming Conventions
- CamelCase for class names
- snake_case for variables and function names
- UPPERCASE for constants
- Descriptive names that reflect purpose 