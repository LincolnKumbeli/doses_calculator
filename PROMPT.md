# Custom Prompt for AI Development Guide

## Core Guidelines

- Do not remove any code or functionality unless explicitly stated
- Add, refine, and improve functionality and appearance while enhancing user experience
- Respect existing structure and logic
- Provide clear explanations for modifications

## Required Reading
- STRUCTURE.md - Core application structure that must be maintained
- PNG Standard Treatment Book 10th Edition 2016
- Drug Doses Frank Shann 17th Edition 2017-1

## Reference Documents

- **PNG Standard Treatment Book 10th Edition 2016**: [Available here](../docs/PNG-Standard-Treatment-Book-10th-edition-2016.pdf)
  - Source for footnotes and condition-specific drug lists
  - Primary reference for PNG healthcare context

- **Drug Doses Frank Shann 17th Edition 2017-1**: [Available here](../docs/Drug-Doses-Frank-Shann-17th-Edition-2017-1.pdf)
  - Primary source for dosage instructions
  - Reference for drug calculations

## Usage Instructions

### 1. Medical Content
- Generate footnotes from PNG Standard Treatment Book
- List condition-appropriate drugs from PNG guidelines
- Use Frank Shann for dosage calculations
- Resolve conflicts with user input

### 2. Implementation Rules
- Verify changes against STRUCTURE.md requirements
- Maintain core functionality as defined
- Preserve essential page elements
- Create formulas based on Frank Shann instructions
- Add drugs to master list maintaining format
- Use PNG guidelines for disease protocols
- Ensure dose consistency across conditions

### 3. Conflict Resolution
- Prompt for choice between conflicting sources
- Default to PNG guidelines if Frank Shann silent
- Document source of each dosage calculation
- Note any deviations from standards

## Example Usage

### Adding New Drug

## Adding New Disease Conditions

Follow these steps exactly to add a new disease condition:

1. Backend Implementation (main.py):
   - Add the disease to the `disease_drugs` dictionary with required medications
   - Add disease-specific footnotes to `disease_footnotes` dictionary
   - Ensure all medications exist in `get_master_doses()` function
   - Add any new drug calculations to `get_master_doses()`
   - Test that all drug calculations work correctly

2. Frontend Updates (disease.html):
   - Add the new disease to the diseases list in alphabetical order
   - Ensure proper ID and value attributes in radio buttons
   - Verify proper display formatting

3. Drug Definition Checklist:
   - [ ] Define all required medications in master_doses
   - [ ] Include proper dosage calculations
   - [ ] Add weight-based formulas
   - [ ] Include any fixed-dose medications
   - [ ] Add any special instructions or warnings

4. Clinical Guidelines Integration:
   - [ ] Add relevant clinical footnotes
   - [ ] Include monitoring requirements
   - [ ] Add warning signs if applicable
   - [ ] Include duration of treatment
   - [ ] Note any contraindications

5. Testing Steps:
   - [ ] Verify disease appears in selection list
   - [ ] Test calculations with various weights
   - [ ] Verify footnotes display correctly
   - [ ] Check all drug doses calculate properly
   - [ ] Test edge cases (very low/high weights)

Example Implementation:
