# Beehive  
<img align="left" src="static/favicon.png" width="30" title="Beehive Logo" alt="Beehive Logo">

A Data Federation Approach to Analyze Behavioral Health and Complement Healthcare Practice with Community Health Metrics  

## Project Description  

This project aims to analyze behavioral health and complement healthcare practice with community health metrics in Alaska using a data federation approach. By leveraging data from various sources, we can gain insights into behavioral health patterns and improve healthcare practices in the community.  

## Tech Stacks Used  
- **Backend**: Flask (Python)
- **Frontend**: React (TypeScript) in `frontend/`
- **Database**: MongoDB
- **Auth**: Clerk REST API
- **Storage**: Local filesystem for media uploads in `static/uploads/` with PDF thumbnails in `static/uploads/thumbnails/`
  
## Workflow
```mermaid
graph TD;
  User["User uploads an image with title, description, sentiment & voice note"] -->|POST request| Backend[Flask Backend]
  Backend -->|Stores metadata| MongoDB[MongoDB Database]
  Backend -->|Stores image & voice note| StaticFolder[Static Folder]
  Admin["Admin views uploaded images & metadata"] -->|GET request| Backend
  Backend -->|Fetches data| MongoDB
  Backend -->|Serves images & voice notes| StaticFolder
  User & Admin -->|Authenticated| Auth[Flask Authentication]

```

## Setup Instructions  

If you want to run this project locally, see the [setup.md](docs/setup.md).  

## Contributing  

**Note**: `dev` branch is our primary development branch. The `main` branch is our stable branch. Please create pull requests against the dev branch if you are contributing to ongoing development. For specific contribution guidelines, see the [contributing.md](docs/contributing.md).  
> **NOTE:**  
> We currently have **two active branches** for development:  
>  
> - **`dev` Branch** – General development and feature updates.  
> - **`modular` Branch** – Focused on modularizing the codebase.  
>  
> You are welcome to contribute to **either of these branches** based on your interest.  
> The **`main` branch is frozen** for direct commits and only pull requests from a stable development branch (dev, modular, ...) are merged into the main branch.  


## License  

This project is licensed under the BSD-3-Clause License. See the [LICENSE](LICENSE) file for more details.
