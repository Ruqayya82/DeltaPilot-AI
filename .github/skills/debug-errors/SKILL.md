---
name: debug-errors
description: '**WORKFLOW SKILL** — Debug and fix errors in code across programming languages and frameworks. USE FOR: reproducing errors, analyzing root causes, applying targeted fixes, validating solutions. DO NOT USE FOR: general coding questions, feature implementation, performance optimization.'
---

# Debug Errors

A comprehensive workflow for systematically debugging and fixing errors in software projects, with language-specific guidance for Python, Java, and JavaScript.

## Prerequisites
- Access to the codebase and error logs
- Ability to run code/tests in the environment
- Basic understanding of the programming language/framework

## Workflow Steps

### 1. Error Reproduction
**Goal**: Confirm the error can be reliably reproduced.

**Actions**:
- Run the failing code/test case
- Note exact steps to reproduce
- Document environment (OS, versions, dependencies)
- Capture error message, stack trace, and any logs

**Language-Specific**:
- **Python**: Use `mcp_pylance_mcp_s_pylanceRunCodeSnippet` to test code snippets
- **Java**: Use `debug_java_application` to launch in debug mode
- **JavaScript**: Run in Node.js or browser dev tools

**Decision Point**: If cannot reproduce, gather more context or ask for reproduction steps.

### 2. Initial Analysis
**Goal**: Understand the error type and immediate context.

**Actions**:
- Parse error message for clues (type, location, cause)
- Check recent changes that might have introduced the error
- Review code at the error location
- Use tools like `get_errors` to check for compile/lint issues

**Language-Specific Tools**:
- **Python**: `mcp_pylance_mcp_s_pylanceFileSyntaxErrors` for syntax checks, `mcp_pylance_mcp_s_pylanceSyntaxErrors` for snippets
- **Java**: `get_errors` for compile errors, `list_jdks` for environment checks
- **JavaScript**: ESLint or TypeScript compiler for static analysis

**Common Error Types**:
- Syntax errors: Check code structure
- Runtime errors: Examine variable states, logic flow
- Import/dependency errors: Verify installations, paths
- Logic errors: Review algorithm, data flow

### 3. Root Cause Investigation
**Goal**: Identify the underlying cause.

**Actions**:
- Trace execution path leading to error
- Check variable values and data states
- Test assumptions about inputs/outputs
- Use debugging tools (breakpoints, logging) if available
- Search for similar issues in codebase or documentation

**Techniques**:
- Divide and conquer: Isolate problematic sections
- Binary search: Comment out code sections to narrow down
- Logging: Add temporary debug prints
- Unit testing: Test individual components

**Language-Specific Debugging**:
- **Python**: Use `evaluate_debug_expression` if debugger attached, or print statements
- **Java**: Use `get_debug_variables`, `get_debug_stack_trace`, `debug_step_operation`
- **JavaScript**: Browser dev tools or Node.js inspector for runtime inspection

### 4. Hypothesis Formation
**Goal**: Develop targeted fix ideas.

**Actions**:
- List 2-3 most likely causes
- Research solutions for similar errors
- Consider edge cases and boundary conditions
- Evaluate impact of potential fixes

### 5. Fix Implementation
**Goal**: Apply minimal, targeted changes.

**Actions**:
- Implement the most promising fix first
- Make changes incrementally
- Test immediately after each change
- Use version control to track changes

**Best Practices**:
- Fix root cause, not symptoms
- Maintain code quality and style
- Add comments explaining the fix
- Update tests if applicable

**Language-Specific Fixes**:
- **Python**: Use `mcp_pylance_mcp_s_pylanceInvokeRefactoring` for code fixes
- **Java**: Ensure classpath and dependencies are correct
- **JavaScript**: Check module imports and transpilation

### 6. Validation
**Goal**: Confirm the fix works and doesn't break anything.

**Actions**:
- Reproduce original error scenario - should now pass
- Run existing tests to ensure no regressions
- Test edge cases and related functionality
- Check for side effects in dependent code

**Language-Specific Validation**:
- **Python**: Run with `mcp_pylance_mcp_s_pylanceRunCodeSnippet` or pytest
- **Java**: Use `run_in_terminal` with Maven/Gradle tests
- **JavaScript**: Run with npm scripts or Jest

### 7. Documentation and Cleanup
**Goal**: Record the solution and clean up.

**Actions**:
- Document the error, cause, and fix in issue tracker or comments
- Remove temporary debug code/logs
- Update documentation if error was due to misunderstanding
- Consider preventive measures (additional tests, code reviews)

## Quality Checks
- [ ] Error is fully resolved
- [ ] No new errors introduced
- [ ] Code follows project standards
- [ ] Tests pass (existing and new)
- [ ] Solution is documented

## Common Pitfalls
- Fixing symptoms instead of root cause
- Making changes without testing
- Not considering edge cases
- Failing to validate in full environment
- Not documenting the resolution

## Related Skills
- testing-strategies (for creating validation tests)
- code-review (for preventing similar errors)