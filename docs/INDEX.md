# Documentation Index

Welcome to the Utility Bills Data Extraction System documentation.

## Getting Started

If you're new to this project, start here:

1. **[Quick Start Guide](QUICK_START.md)** - Get up and running in minutes
   - Installation instructions
   - Basic usage examples
   - Common workflows
   - Troubleshooting basics

2. **[Main README](README.md)** - Comprehensive system overview
   - What the system does
   - Architecture and components
   - List of all supported providers
   - How the extraction workflow works

## Reference Documentation

### For Users

**[Data Structure Reference](DATA_STRUCTURE.md)** - Understanding the output
- Complete JSON structure explanation
- Field definitions and examples
- Working with the extracted data
- Python and SQL examples

**[Provider-Specific Notes](PROVIDER_NOTES.md)** - Special considerations
- Details for each major provider
- Bill format variations (e.g., SCL residential vs commercial)
- Common issues and solutions
- Testing guidelines

### For Developers

**[Main README](README.md)** - Development information
- System architecture
- Adding new providers (step-by-step guide)
- Core components explained
- Design principles

**[Data Structure Reference](DATA_STRUCTURE.md)** - Schema details
- Pydantic model structure
- Field types and constraints
- Validation objects
- Null value handling

## Quick Links by Task

### I want to...

**Process my first bill**
→ Start with [Quick Start Guide](QUICK_START.md)

**Understand the JSON output**
→ Read [Data Structure Reference](DATA_STRUCTURE.md)

**Add a new utility provider**
→ See "Adding a New Provider" in [Main README](README.md#adding-a-new-provider)

**Troubleshoot an extraction failure**
→ Check [Quick Start Guide - Troubleshooting](QUICK_START.md#troubleshooting) and [Provider Notes - Common Issues](PROVIDER_NOTES.md#common-issues)

**Work with Seattle City Light bills**
→ Read [Provider Notes - Seattle City Light](PROVIDER_NOTES.md#seattle-city-light)

**Export data to CSV or database**
→ See examples in [Quick Start Guide - Common Workflows](QUICK_START.md#common-workflows)

**Understand validation failures**
→ Review [Data Structure - Validation Objects](DATA_STRUCTURE.md#total-amount-validation-object) and [Provider Notes - Validation](PROVIDER_NOTES.md#issue-validation-failures)

**See the complete list of supported providers**
→ Check [Main README - Supported Providers](README.md#supported-utility-providers)

**Learn about the system architecture**
→ Read [Main README - System Architecture](README.md#system-architecture)

## Document Summaries

### [README.md](README.md)
**Main documentation file**  
Contains: Overview, features, architecture, supported providers, workflow explanation, directory structure, adding providers, configuration, design principles

**Best for:** Understanding the system as a whole, reference for supported providers, guide for extending the system

### [QUICK_START.md](QUICK_START.md)
**Hands-on getting started guide**  
Contains: Installation, setup, basic usage, example scripts, common workflows, troubleshooting

**Best for:** New users, quick reference, practical examples, solving common problems

### [DATA_STRUCTURE.md](DATA_STRUCTURE.md)
**JSON output schema reference**  
Contains: Complete data structure, field definitions, examples, working with data, provider variations

**Best for:** Understanding extracted data, writing code to process JSON, database design, data analysis

### [PROVIDER_NOTES.md](PROVIDER_NOTES.md)
**Provider-specific documentation**  
Contains: Special considerations per provider, bill format variations, common issues, testing guidelines

**Best for:** Troubleshooting provider-specific issues, understanding bill format differences, adding/testing providers

## Documentation by Audience

### End Users
People who just want to extract data from their bills:
1. [Quick Start Guide](QUICK_START.md) - Setup and basic usage
2. [Data Structure Reference](DATA_STRUCTURE.md) - Understanding the output
3. [Quick Start - Troubleshooting](QUICK_START.md#troubleshooting) - Fixing common issues

### Data Analysts
People working with the extracted data:
1. [Data Structure Reference](DATA_STRUCTURE.md) - Complete schema
2. [Quick Start - Common Workflows](QUICK_START.md#common-workflows) - Example scripts
3. [Provider Notes](PROVIDER_NOTES.md) - Understanding variations

### Developers
People extending or maintaining the system:
1. [Main README](README.md) - Architecture and components
2. [Main README - Adding Providers](README.md#adding-a-new-provider) - Extension guide
3. [Provider Notes](PROVIDER_NOTES.md) - Provider implementation details
4. [Data Structure Reference](DATA_STRUCTURE.md) - Data models

## File Locations Reference

### Source Code
- **Main extractor**: `src/utility_bills/extractor.py`
- **Provider router**: `src/utility_bills/provider_router.py`
- **Prompts**: `src/utility_bills/prompts/*.txt`
- **Pydantic models**: `src/utility_bills/pydantic_models/*.py`
- **Provider functions**: `src/utility_bills/provider_functions/*.py`

### Data Directories
- **Inbox** (place PDFs here): `src/data/inbox/`
- **Processed JSON**: `src/data/processed/json/`
- **Processed PDFs**: `src/data/processed/pdf/`
- **Unprocessed JSON**: `src/data/unprocessed/json/`
- **Unprocessed PDFs**: `src/data/unprocessed/pdf/`

### Logs
- **Application logs**: `logs/utility_bills.log`

### Configuration
- **Dependencies**: `requirements.txt`
- **Environment**: System environment variables (OPENAI_API_KEY)

## Additional Resources

### External Documentation
- [OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs) - Understanding the extraction API
- [Pydantic Documentation](https://docs.pydantic.dev/) - Data validation library
- [Python Logging](https://docs.python.org/3/library/logging.html) - Logging system

### Project Files
- **Requirements**: `requirements.txt` - All Python dependencies
- **Logs**: `logs/utility_bills.log` - Detailed processing logs

## Documentation Updates

When updating documentation:

1. **Keep it current**: Update "Last Updated" dates
2. **Cross-reference**: Link between related sections
3. **Add examples**: Include code snippets and output samples
4. **Note breaking changes**: Highlight API or structure changes
5. **Update this index**: Reflect new sections or documents

## Getting Help

### Troubleshooting Steps

1. **Check the logs**  
   Location: `logs/utility_bills.log`  
   Look for: Error messages, stack traces, extraction results

2. **Review relevant documentation**
   - Extraction failure → [Quick Start - Troubleshooting](QUICK_START.md#troubleshooting)
   - Data questions → [Data Structure Reference](DATA_STRUCTURE.md)
   - Provider-specific → [Provider Notes](PROVIDER_NOTES.md)

3. **Verify setup**
   - API key set correctly
   - Dependencies installed
   - Correct Python version (3.10+)

4. **Test with known-good file**
   - Use a processed example from `src/data/processed/pdf/`
   - Verify basic functionality works

5. **Check provider support**
   - Is your provider in the [supported list](README.md#supported-utility-providers)?
   - Are there special notes in [Provider Notes](PROVIDER_NOTES.md)?

## Version History

### Version 2.1 (January 2026)
- Added Seattle City Light commercial format support
- Implemented automatic format detection
- Created comprehensive documentation suite
- 30+ utility providers supported

### Earlier Versions
- Phase 1: Initial proof of concept
- Phase 2: Production system with multiple providers

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ UTILITY BILLS EXTRACTION SYSTEM - QUICK REFERENCE   │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Setup:                                              │
│  1. Set OPENAI_API_KEY environment variable        │
│  2. pip install -r requirements.txt                │
│                                                     │
│ Process Bills:                                      │
│  1. Drop PDFs in: src/data/inbox/                  │
│  2. Run: extractor.process_inbox()                 │
│  3. Check: src/data/processed/json/                │
│                                                     │
│ Output Structure:                                   │
│  • statement_level_data (financials)               │
│  • account_level_data (account info)               │
│  • meter_level_data (usage & charges)              │
│                                                     │
│ Validation:                                         │
│  • Check is_match fields in JSON                   │
│  • Review difference values                        │
│  • See logs for details                            │
│                                                     │
│ Logs: logs/utility_bills.log                       │
│ Docs: docs/                                         │
│ Help: See QUICK_START.md for troubleshooting       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

**Documentation Version**: 1.0  
**Last Updated**: January 2026  
**System Version**: 2.1
