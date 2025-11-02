# WordStream Maker - Local Setup Guide

## Quick Start

WordStream Maker is a lightweight, frontend-only application that requires NO backend dependencies. You can run it locally in two ways:

### Option 1: Simple Python HTTP Server (Recommended)

1. Navigate to the maker-wordstream directory:
```bash
cd "C:\Users\ferra\DevProjects\FirstMondayScraperV2\maker-wordstream"
```

2. Start a local HTTP server:
```bash
python -m http.server 8000
```

3. Open your browser and visit:
```
http://localhost:8000
```

4. You should see the WordStream Maker interface

### Option 2: Python's Built-in Server (Alternative)

```bash
cd "C:\Users\ferra\DevProjects\FirstMondayScraperV2\maker-wordstream"
python -m http.server 8080
```

Then visit: `http://localhost:8080`

### Option 3: Use Node.js (if installed)

```bash
cd "C:\Users\ferra\DevProjects\FirstMondayScraperV2\maker-wordstream"
npx http-server
```

## Data Format

WordStream Maker expects CSV or TSV data with the following structure:

```
TimeUnit, TextColumn, [optional metadata columns]
```

Example:
```
Year, FullText, Author, Category
1996, "Text content here...", "Author Name", "Category"
1997, "More text...", "Another Author", "Category"
```

## Project Files

```
maker-wordstream/
├── index.html          # Main application interface
├── css/                # Styling
├── lib/                # Libraries (D3.js, etc.)
├── src/                # JavaScript source code
├── data/               # Sample datasets
└── assets/             # Images and resources
```

## Your First Monday Data

The prepared data file will be located at:
```
maker-wordstream/data/firstmonday-yearly-texts.csv
```

This file contains:
- Year (1996-2025)
- Full combined text for each year
- Word/phrase frequency counts

## Using WordStream Maker

1. Open http://localhost:8000 in your browser
2. Click "Import Data" or drag/drop the CSV file
3. Select your time column (Year)
4. Select your text column (FullText)
5. Configure visualization options
6. Generate your wordstream visualization
7. Export or save your analysis

## Stopping the Server

Press `Ctrl+C` in the terminal to stop the local server.

## Troubleshooting

- **Port already in use**: Change port number (e.g., 8001, 8080, 9000)
- **CORS errors**: This shouldn't occur with local file serving, but if it does, ensure you're using the http.server method
- **Browser shows "Cannot GET /"**: Make sure you're in the correct directory (maker-wordstream)

## More Information

- Live demo: https://huyen-nguyen.github.io/maker/
- GitHub: https://github.com/huyen-nguyen/maker
- Paper: https://arxiv.org/pdf/2209.11856.pdf
