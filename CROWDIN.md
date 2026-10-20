# How to setup Crowdin

## Creating the Crowdin project

Crowdin projects can now be created automatically from Github! 

They have been configured to have some default settings, including the ten most commonly-used target languages, and following this naming convention: `RPF-Project-Name-of-Repo`.

### To create a Crowdin project:

1. Go to the `Actions` tab on the Github repository.

2. On the left sidebar, go down to `Create Crowdin project`

3. On the right-hand side, there is a button labelled `Run workflow`. Click into the dropdown menu and press `run workflow`, making sure that `Branch: master` is selected.

4. Within a minute or so, the project should appear in Crowdin! 🎉

> [!TIP]
> To be able to download and upload translation from Crowdin, you will need to follow the steps below to setup continous integration with Github.

## Integrating with Github

To make use of the Github workflows in this project repository for automating translation setup, you need to add the project's Crowdin ID to the repository's secrets on Github.

Once this is done, files will upload to Crowdin every time a PR is merged into `master`. Download will happen daily at 1am UTC, or when manually triggered from the `Actions` tab, which creates a PR with all the updated tranlsation files. 

### Adding the project ID to Github

1. Once the project is created on Crowdin, copy the project ID. 

    - You should find this on the project's Crowdin dashboard, in a grey box on the right-hand side of the screen. It will be in the `Details` field, in the format `ID: 818746`. You just need the number.

2. In the Github repository for the project, go to `Settings`, then `Secrets and variables` which is in the `Security` section.

3. Click `Actions` and then go down to the `Repository secrets` section. 

4. Click to add a `New repository secret`.

5. **Enter the secret name, which should be `CROWDIN_PROJECT_ID`**

6. Paste the project ID number into the `Secret` field.

7. Press `Add secret` and you're done!

## Post-processing translations using NTTT

[The NTTT script](https://github.com/raspberrypilearning/nttt) for tidying up translation files downloaded from Crowdin can be also run using GitHub Actions. It can be manually triggered from the `Actions` tab with the workflow `NTTT processing` 

> [!NOTE]
> The NTTT script does not fix all the errors introduced during Crowdin export. Some of them can be fixed by using Crowdin `Configurable JSON&YAML` and `Custom Post-Export Processor`. Eventually, they will be handled by either updated NTTT or another script that runs from GitHub Actions. 


## Any questions?

Please reach out to the Code Club projects team with any comments or questions! 
