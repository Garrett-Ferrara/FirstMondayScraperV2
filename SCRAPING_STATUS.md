# Full Corpus Scraping - In Progress

## Status

**Started:** October 19, 2025, 20:47 UTC
**Mode:** Full corpus (all 359 issues)
**Process:** Running in background

## Monitoring Progress

### Quick Check

```bash
python check_progress.py
```

Shows:
- Issues processed (X / 359)
- Articles processed
- Recent issues scraped
- Error summary

### View Live Log

```bash
# Last 50 lines
tail -50 scrape_output.log

# Follow live updates
tail -f scrape_output.log

# View full log
cat scrape_output.log
```

### Check Checkpoint

```bash
cat data/checkpoint.json
```

## Expected Timeline

Based on testing (~8-10 seconds per article, avg 8 articles per issue):

- **Per issue:** ~1-2 minutes
- **Full corpus (359 issues):** ~6-12 hours
- **Current rate:** Check with `python check_progress.py`

## Output Organization

All data organized by issue date:

```
data/
├── Full Text/
│   ├── 1 September 2025/
│   ├── 6 May 1996/
│   └── ...
└── Metadata/
    ├── 1 September 2025/
    ├── 6 May 1996/
    └── ...
```

## Progress Checkpoints

The scraper automatically saves progress every issue:
- ✅ Resume-safe (can restart without re-scraping)
- ✅ Skip already-processed issues
- ✅ Tracks articles and issues separately

## If Something Goes Wrong

### Script Stopped?

Check if it's still running:
```bash
ps aux | grep scrape_all.py
```

If stopped, restart (will skip already-processed issues):
```bash
python scrape_all.py > scrape_output_resume.log 2>&1 &
```

### Check for Errors

```bash
grep -i error data/scraper.log | tail -20
```

### Disk Space

Estimated final size: ~20-25GB
```bash
du -sh data/
```

## Real-time Statistics

While scraping, you'll see updates every 10 issues showing:
- Total articles processed
- Successful vs failed
- Total word count
- Skipped issues

## When Complete

The script will print:
```
FULL CORPUS SCRAPING COMPLETE!
```

Then you can:
1. Run `python check_progress.py` for final stats
2. Verify all 359 issues in `data/Full Text/`
3. Analyze the corpus

## Next Steps After Completion

1. ✅ Verify data quality
2. 📊 Generate corpus statistics
3. 👥 Extract author networks
4. 📝 Build citation database
5. 🔍 Corpus analysis

---

**Monitor periodically with:** `python check_progress.py`
