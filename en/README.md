# Project Structure

This repository is used to build CCP projects. Below is the directory structure and a description of what each folder and file is used for.

```plaintext
en/
├── code/
│   ├── project-name-complete/
│   │   ├── main.py
│   │   └── project_config.yml
│   └── project-name-starter/
│       ├── main.py
│       └── project_config.yml
├── images/
│   └── .keep
├── resources/
│   └── .keep
├── solutions/
│   └── .keep
├── README.md
├── meta.yml
├── step_1.md
├── step_2.md
└── step_3.md
```

## Directory and File Descriptions

### `code/`
Contains Python or HTML code used in the Raspberry Pi Code Editor.  
- Each project must be in its own subdirectory. Directory names should be descriptive but are otherwise flexible.  
- Inside each subdirectory:  
  - `main.py` (for Python projects) or `index.html` (for HTML projects)  
  - `project_config.yml` containing:  
    - `name`: The project name  
    - `identifier`: A unique identifier for the project
    - `type`: 'python' or 'html'  
    - `build`: `false` by default; set to `true` for the editor project to be built  

### `images/`
Stores all images for the project.  
- Must contain a `banner.png` (the project’s hero image).  
- Edited images should be accompanied by their original versions.  
- Additional supporting images should be sensibly named.  

### `resources/`
Contains supporting resources for the project.  
- Must include the PDF version of the project, clearly named.  
- Other resources such as offline starter projects, assets, or supporting files can also go here.  
- Learners can download a `.zip` of this folder via:  
  `https://rpf.io/p/en/project-slug-go`

### `solutions/`
Contains the final completed version of the project, if needed.  
- Learners can download this via:  
  `https://rpf.io/p/en/project-slug-get`

### `meta.yml`
Defines project metadata used for publishing. Example fields:  
```yaml
title: Project title in sentence case
hero_image: images/banner.png
description: A short description of the project
listed: false
pdf: false
steps:
  - title: What you will make
  - title: Step title
    completion:
      - engaged
  - title: Step title
    completion:
      - internal      
  - title: Challenge
    challenge: true
    completion:
      - external
```

- **`listed`**:  
  - `true`: project is published from the master branch  
  - `false`: project is not publicly listed (but still accessible via slug URL)  
- **`pdf`**: Path to a PDF in `resources/`, making it downloadable  
- **`completion`**: Metrics for learner progress  
  - `engaged`: Learner has reached the first "making" step  
  - `internal`: Final "making" step of the project  
  - `external`: Last step of the project, often a challenge  
- **Challenges**: Optional, provide extra tasks and count as `external` completion steps  

### `README.md`
Documentation for the project, including the structure and explanation of contents.

### `step_1.md`, `step_2.md`, `step_3.md`
Markdown files containing step-by-step instructions for learners.  
- Each step corresponds to a tutorial section.  
- The number of steps varies by project.  
