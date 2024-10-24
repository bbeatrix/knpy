1. Clone the Repository
If you haven't already cloned the repository, clone it to your local machine:

    git clone <repository-url>

This creates a local copy of the repository on your machine.

2. Create a New Branch (Development Branch)
Since the main branch is protected, you cannot push directly to it. You need to create a new branch for your work. First, make sure you are on the latest version of the main branch:

    git checkout main
    git pull origin main  # Ensure your local main is up to date

Now, create and switch to a new development branch. This branch can be named based on the feature you're working on:

    git checkout -b <your-branch-name>

3. Make Changes
Now, you're on your own development branch. Make the necessary code changes, add files, and test your changes locally.

4. Stage and Commit Your Changes
Once you're satisfied with the changes, add them to the staging area and commit them:

    git add .
    git commit -m "Add feature/new-awesome-feature"

Be sure to write a meaningful commit message describing what changes you’ve made.

5. Push Your Branch to the Remote Repository
Push your development branch to the remote repository:

    git push origin <your-branch-name>

6. Create a Pull Request (PR)
Now that your branch is pushed to the remote repository, go to the repository's website (e.g., GitHub, GitLab, Bitbucket) and create a Pull Request (PR) to merge your branch into the main branch.

Go to the Pull Requests section.
Click on New Pull Request.
Select your branch as the source and the protected main branch as the target.
Add a title and a description explaining your changes.
Request reviewers (if applicable).

7. Wait for Code Review
Since the main branch is protected, other team members (or maintainers) will likely review your pull request. They may request changes or approve your PR.

8. Incorporate Feedback (If Necessary)
If your reviewers request changes, make the necessary updates:

Checkout your feature branch again.
Apply the changes.
Commit and push the updates:

    git add .
    git commit -m "Incorporate PR feedback"
    git push origin <your-branch-name>

The pull request will automatically update with your new commits.

9. Merge the Pull Request
Once your pull request is approved, you or a maintainer can merge the PR into the main branch. This can usually be done with the Merge button on the platform (e.g., GitHub).

10. Clean Up (Optional)
After your PR is merged, you can delete your local and remote feature branch:

Delete the remote branch:

    git push origin --delete <your-branch-name>

Delete your local branch:

    git branch -d <your-branch-name>

11. Pull the Latest Changes from Main
Finally, to sync your local environment with the latest version of main, pull the changes:

    git checkout main
    git pull origin main

**Summary of Commands**

Clone the repo:
    git clone <repository-url>
Create a new branch:
    git checkout -b <your-branch-name>
Stage and commit changes:
    git add .
    git commit -m "Your commit message"
Push the branch:
    git push origin <your-branch-name>
Create a pull request and wait for review.

This workflow ensures that the main branch remains protected, and all changes are peer-reviewed before being merged into the main codebase.
