# AI Agent Guidelines for Lesson Organizer Project

## Overview
This document provides guidelines for AI agents working on the Lesson Organizer project. These guidelines ensure consistency, quality, and maintainability of code changes.

## Required Analysis for Code Changes

### Benefits and Drawbacks Analysis
**MANDATORY**: Whenever making changes to the codebase, AI agents must include:

1. **Benefits Section**: Explain the advantages of the implemented solution
   - Performance improvements
   - Security enhancements
   - Maintainability gains
   - User experience improvements
   - Code clarity/readability improvements

2. **Drawbacks Section**: Honestly assess potential downsides of the implementation
   - Performance costs
   - Increased complexity
   - Potential maintenance burden
   - Breaking changes or compatibility issues
   - Resource usage implications

### Example Format:
```
## Benefits of This Change
- Improved security by preventing exposure of sensitive user data
- Clear separation of concerns between full user data and public profile data
- Maintainable approach that's easy to modify in the future

## Potential Drawbacks
- Slight increase in schema complexity with additional UserRelationshipSchema
- Need to remember to use the correct schema in different contexts
- Potential confusion for new developers about which schema to use when
```

## Code Style Guidelines

### General Code Commenting
- **No inline comments**: Place comments above the relevant line(s), never on the same line as code
- Comments should explain **why**, not **what** the code does
- Use clear, concise language without unnecessary words
- Avoid obvious comments that don't add value

### Backend (Flask/Python)
- Follow PEP 8 style conventions
- Use type hints where beneficial
- Write descriptive docstrings for classes and complex methods
- Prefer explicit over implicit (clear variable names, explicit imports)
- Use meaningful exception messages
- Implement proper error handling and logging

### Frontend (Svelte)
- Use Svelte 5 runes syntax ($state, $effect, $derived, etc.)
- Prefer composition over inheritance
- Use TypeScript for type safety
- Follow consistent naming conventions (camelCase for variables, PascalCase for components)
- Write semantic HTML with proper accessibility attributes

### Database/Models
- Use descriptive table and column names
- Include proper foreign key relationships and constraints
- Add database indexes for frequently queried fields
- Use migrations for all schema changes
- Document complex relationships and business logic

## Security Considerations
- Never expose sensitive data (passwords, tokens, private keys) in API responses
- Validate all user inputs on both client and server side
- Use proper authentication and authorization checks
- Follow principle of least privilege
- Sanitize data before database operations

## Testing Requirements
- Write unit tests for new business logic
- Include integration tests for API endpoints
- Test error conditions and edge cases
- Verify security constraints are enforced
- Update existing tests when modifying functionality

## Documentation Standards
- Update API documentation when changing endpoints
- Document breaking changes in commit messages
- Include examples in complex function docstrings
- Maintain README files for setup and deployment instructions
- Document configuration options and environment variables

## Performance Considerations
- Consider database query efficiency (N+1 problems, proper indexing)
- Minimize API response payload size
- Use appropriate caching strategies
- Consider memory usage in data processing
- Profile performance-critical code paths

## Error Handling
- Provide meaningful error messages to users
- Log detailed error information for debugging
- Use appropriate HTTP status codes
- Handle edge cases gracefully
- Implement proper fallback mechanisms

## Architecture Principles
- Maintain separation of concerns
- Keep business logic in service layers
- Use consistent patterns across the codebase
- Avoid tight coupling between components
- Design for scalability and maintainability

## Communication Guidelines
- **No flattery or excessive praise**: Provide direct, honest feedback and explanations
- Explain technical decisions and trade-offs objectively
- Provide context for complex changes without unnecessary embellishment
- Suggest alternative approaches when appropriate
- Highlight areas that may need future attention
- Be transparent about limitations and assumptions
- Focus on facts and technical merits rather than subjective praise

## Review Process
Before implementing changes, consider:
- Are there existing patterns that should be followed?
- Will this change affect other parts of the system?
- Is this the simplest solution that meets the requirements?
- Are there any security implications?
- How will this change be tested and verified?

## Commit Message Format
Use clear, descriptive commit messages that explain:
- What was changed
- Why it was changed
- Any breaking changes or migration requirements

Example:
```
feat: Add UserRelationshipSchema to hide private user fields

- Created separate schema for user data in relationships
- Updated LessonSchema and UserLessonSchema to use new schema
- Prevents exposure of passwords and sensitive data in API responses

Breaking change: User objects in relationship fields now return fewer fields
```