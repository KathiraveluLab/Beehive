# Contributing
If you are looking to contribute to this project, follow these steps:

1. **Fork the Repository**: Click the "Fork" button at the top right of the repository page to create a copy of the repository under your GitHub account.

2. **Clone the Repository**: Clone the forked repository to your local machine using the following command:
    ```bash
    git clone https://github.com/<your-username>/Beehive.git
    ```
    Replace `<your-username>` with your GitHub username.

3. **Create a New Branch**: Navigate to the cloned repository and create a new branch for your work. Use a descriptive name for the branch, such as `dev`:
    ```bash
    cd Beehive
    git checkout -b dev
    ```

4. **Make Your Changes**: Implement your changes in the new branch. Ensure your code follows the project's coding standards and includes appropriate tests.

5. **Commit Your Changes**: Commit your changes with signoff and a clear and concise commit message:
    ```bash
    git add .
    git commit -s -m "Add detailed description of your changes"
    ```

6. **Push Your Changes**: Push the changes to your forked repository on GitHub:
    ```bash
    git push origin dev
    ```

7. **Open a Pull Request**: Go to the original repository on GitHub and open a pull request. Provide a meaningful title and description for your pull request, detailing the changes you have made and any relevant information.

        **Sample Pull Request Template**:
        ```markdown
        ### Description

        Please include a summary of the changes and the related issue. Please also include relevant motivation and context.

        ### Type of Change

        - [ ] Bug fix (non-breaking change which fixes an issue)
        - [ ] New feature (non-breaking change which adds functionality)
        - [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
        - [ ] Documentation update

        ### Checklist

        - [ ] My code follows the style guidelines of this project
        - [ ] I have performed a self-review of my own code
        - [ ] I have commented my code, particularly in hard-to-understand areas
        - [ ] I have made corresponding changes to the documentation
        - [ ] My changes generate no new warnings
        - [ ] I have added tests that prove my fix is effective or that my feature works
        - [ ] New and existing unit tests pass locally with my changes
        - [ ] Any dependent changes have been merged and published in downstream modules

        ### Additional Information

        Add any other information or screenshots about the pull request here.
        ```

8. **Review Process**: Wait for the project maintainers to review your pull request. Be responsive to any feedback or requested changes.

9. **Merge**: Once your pull request is approved, it will be merged into the main branch by the maintainers.

Thank you for contributing to this project!
