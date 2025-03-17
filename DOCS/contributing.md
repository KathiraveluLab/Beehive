# Community Contribution Guide

Thank you for considering contributing to our project! To ensure a smooth collaboration, please follow these guidelines when submitting contributions.

## Before commiting it is recommended to run:
```bash
pre-commit run --all-files
```
This will ensure that black, flake and isort is run.

## 1. Sign off your commits

We require contributors to **sign off** their commits to ensure that the commits are made in compliance with our Contributor License Agreement (CLA). This also helps maintain clarity about who made the changes.

### How to sign off your commit:
To sign off your commit, use the `--signoff` flag when committing, like so:

```bash
git commit --signoff --message "Your message"
(or)
git commit -s -m "Your message"
```

This will add a `Signed-off-by` line at the end of your commit message, confirming that you have read and agreed to the CLA.

Example commit message with sign-off:
```
Fix issue with login form validation

- Corrected a bug that prevented the validation from triggering on empty fields.

Signed-off-by: Jane Doe <jane.doe@example.com>
```

## 2. Write Effective Commit Messages

Clear, concise, and meaningful commit messages help maintain a readable history of changes. Follow these guidelines for writing commit messages:

- **Use present tense**: Commit messages should describe what *this commit does*, not what *it did* (e.g., "Fix bug in validation logic" rather than "Fixed bug").
- **Be descriptive, but concise**: Summarize what you changed and why in a single line if possible. If more detail is needed, provide additional explanation in the body of the message.

### Example Commit Message:
```
Fix user authentication issue after password reset

- Users were unable to log in after resetting their password due to a session mismatch.
- Added a check to synchronize the session after a password reset.
```

## 3. Create Meaningful Pull Request Titles and Descriptions

When submitting a pull request (PR), it's important to make the title and description clear and easy to understand. Here's how to do it:

### Pull Request Title:
- **Be specific**: Clearly describe what the pull request accomplishes. 
- **Use imperative mood**: Like with commit messages, use the present tense (e.g., "Add new login screen" instead of "Added new login screen").

### Example PR Title:
```
Fix user authentication issue after password reset
```

### Pull Request Description:
Provide a detailed explanation of the following in your PR description:
- **What**: A brief overview of the change you made.
- **Why**: Explain why this change is necessary.
- **How**: If applicable, provide context on how you implemented the change.

### Example PR Description:
```
## What:
This pull request fixes an issue where users were unable to log in after resetting their password.

## Why:
Users reported issues with authentication after password reset. This fix ensures the session is synchronized post-reset.

## How:
Added logic to check the session after a password reset and synchronize it with the new user credentials.
```

## 4. General Contribution Tips

- **Keep your branches small and focused**: Try to limit each pull request to a single feature or bug fix.
- **Test your changes**: Run `pytest tests/ --cov=./` and ensure proper test coverage
- **Follow coding standards**: Adhere to project's conventions for naming and structure
- **Be respectful**: Maintain positive and constructive communication

## 5. Code of Conduct

Please ensure that you read and follow our [Code of Conduct](/CODE_OF_CONDUCT.md), which outlines the expectations for respectful and inclusive behavior within the community.

## 6. Questions or Issues?

If you have any questions, feel free to reach out by opening an issue, or ask in the project's discussion channel. We are happy to help!

Thank you for contributing, and we look forward to reviewing your changes!
