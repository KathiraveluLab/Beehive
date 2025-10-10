# Beehive  
<img align="left" src="static/favicon.svg" width="30" title="Beehive Logo" alt="Beehive Logo">

A Data Framework for Behavioral Health with Digitized Drawings and Photographs. 

## Project Description  

This project aims to analyze behavioral health and complement healthcare practice with community health metrics in Alaska using a data federation approach. By leveraging data from various sources, we can gain insights into behavioral health patterns and improve healthcare practices in the community.

## Tech Stacks Used  
- **Language/Framework**: Flask (Python)
- **Authentication**: Google OAuth2
- **Database**: MongoDB
  
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

For instructions to configure and run this project locally, see the [setup.md](docs/setup.md).

## Contributing  

**Note**: `dev` branch is our primary development branch. The `main` branch is our stable branch. Please create pull requests against the dev branch if you are contributing to ongoing development. For specific contribution guidelines, see the [contributing.md](docs/contributing.md).

The **`main` branch is frozen** for direct commits and only pull requests from a stable development branch are merged into the main branch.

