# Changelog

All notable changes to the PNG Drug Doses Calculator will be documented in this file.

## [Unreleased]

## [1.0.0] - 2024-01-18

### Added
- Initial release of PNG Drug Doses Calculator
- Comprehensive drug database with dosage calculations based on Frank Shann 2017 Edition
- Disease-specific drug protocols for:
  - Asthma
  - Conjunctivitis
  - Malaria
  - Meningitis
  - Pneumonia
  - Reactive Airways Disease
  - Sepsis
- Emergency drug calculations
- RSI and ETT drug calculations with tube size guide
- Fluid calculations including:
  - Maintenance rates (4:2:1 Rule)
  - Two-thirds maintenance rates
  - Bolus calculations (10mL/kg, 15mL/kg, 20mL/kg)
  - Parkland formula for burns

### Features
- Bootstrap 5.3.0 responsive design
- Mobile-friendly interface
- Tabulated drug calculation results
- Clinical footnotes and warnings
- Weight-based dosing calculations
- User input validation
- Clear navigation system
- Error handling and user feedback
- Font Awesome icons for better UX

### Technical Features
- Flask web framework
- Local development server
- Template caching disabled
- Responsive layout using Bootstrap grid
- Custom CSS variables for theming
- OrderedDict for consistent drug ordering
- Automatic dose calculations
- Input sanitization and validation
- Error message flashing
- Network-accessible development server

### Drug Database
- Complete pediatric drug formulary
- Dose calculations for:
  - Common antibiotics
  - Emergency medications
  - Sedatives and analgesics
  - Respiratory medications
  - Cardiac medications
  - Fluid therapy
  - Disease-specific protocols

### Recent Updates
- Added Benzhexol with age restrictions and dosing
- Added Baclofen with oral and intrathecal dosing
- Added Benzathine penicillin with unit conversion
- Improved table layout for drug calculations
- Enhanced mobile responsiveness
- Added clinical footnotes for key conditions

## [1.0.1] - 2024-01-18

### Added
- Custom AI development prompt (PROMPT.md)
- Development guidelines for AI assistance
- Safety-first development approach
- PNG-specific enhancement rules

### Modified
- Enhanced changelog structure
- Added version tracking
- Included development focus areas
- Clarified modification guidelines

### Development Notes
- Added AI development guidelines
- Established modification boundaries
- Defined enhancement priorities
- Created structured development prompt

### Development Notes
- Built for PNG healthcare settings
- Based on standard treatment guidelines
- Includes weight-based dose limitations
- All calculations verified against source material

## [1.0.2] - 2024-01-18

### Added
- Comprehensive AI development guide
# ...new changes...

### Documentation
- Added PNG Standard Treatment Book reference
- Added Drug Doses Frank Shann reference
- Added conflict resolution guidelines
- Added example implementations

### Safety
- Added source documentation requirements
- Added dose conflict resolution process
- Added clinical warning requirements
- Added change documentation rules

### Development Notes
- Enhanced development guidelines
- Added medical reference framework
- Improved safety protocols
- Standardized implementation patterns

## [1.0.3] - 2024-01-18

### Added
- New disease condition: Anaemia
- Iron supplementation calculations
- Anaemia-specific clinical footnotes
- Treatment guidelines for iron deficiency

### Clinical Updates
- Added iron therapy protocols
- Added vitamin supplementation
- Added treatment monitoring guidelines
- Added cautions for iron therapy in malaria

## [1.0.4] - 2024-01-18

### Added
- New disease condition: Measles
- Vitamin A dosing by age groups
- Measles-specific clinical footnotes
- Infection control guidelines
- Treatment monitoring protocols

### Clinical Updates
- Added Vitamin A protocol
- Added measles complications monitoring
- Added isolation requirements
- Added eye care guidelines

## [1.0.5] - 2024-01-18

### Reverted
- Reverted recent HTML template changes
- Restored original Bootstrap styling
- Maintained existing functionality
- Kept original color scheme

### Technical Updates
- Followed Custom Prompt guidelines
- Maintained template inheritance
- Preserved existing UI components
- Kept consistent styling across pages

## [1.0.6] - 2024-01-18

### Added
- STRUCTURE.md defining core app structure
- Required structure validation in development process
- Core functionality documentation

### Modified
- Updated PROMPT.md to reference STRUCTURE.md
- Added structure requirements to changelog process
