#!/usr/bin/env python3
"""
CTRL - Environment Control Tool

A general-purpose environment control tool for browser automation, shell commands, and system interaction.

Usage:
    ctrl search "query term"                    # Basic Google search
    ctrl search --new-tab "query"               # Open in new Safari tab
    ctrl search --results 5 "query"             # Parse and return 5 results
    ctrl search --json "query"                  # Return results as JSON
    ctrl surf "https://example.com"             # Open URL in new tab
    ctrl navigate "https://example.com"         # Navigate to URL in current tab
    ctrl new-tab                                # Open new empty tab
    ctrl shell "command"                        # Execute shell command in tmux session

Examples:
    ctrl search "Python documentation"
    ctrl search --new-tab --results 3 "AI research papers"
    ctrl search --json "machine learning tutorials"
    ctrl surf "https://github.com"
    ctrl box "ls -la"
    ctrl box "python script.py"
    ctrl outbox
    ctrl outbox 100
"""

import sys
import os
import argparse
import subprocess
import urllib.parse
import time
import json
import logging
from typing import Optional, List, Dict, Any

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


__version__ = "1.0.0"


def search_google(query: str, max_results: int = None, new_tab: bool = False) -> List[dict]:
    """
    Perform Google search and parse results.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (None for all)
        new_tab: Whether to open search in new Safari tab

    Returns:
        List of dicts with keys: title, url, description, displayUrl, position
    """
    # URL encode the query for Google search
    encoded_query = urllib.parse.quote_plus(query)
    search_url = f"https://www.google.com/search?q={encoded_query}"

    try:
        if new_tab:
            # Create new tab
            subprocess.run(['open', '-a', 'Safari', 'about://'], check=True)
            time.sleep(0.3)

        # Navigate to search URL
        script = f'''
        tell application "Safari"
            set URL of current tab of window 1 to "{search_url}"
        end tell
        '''

        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Failed to navigate to search: {result.stderr}")

        # Wait for page to load
        time.sleep(3)

        # Parse results if requested
        if max_results is not None:
            max_results_param = max_results if max_results > 0 else -1
            search_results = parse_google_results(max_results_param)
            return search_results
        else:
            return []

    except Exception as e:
        logging.error(f"Error in search_google: {e}")
        return []


def parse_google_results(max_results=-1):
    """
    Parse Google search results using semantic patterns rather than HTML structure.

    This approach looks for external links and uses universal patterns that
    Google can't change without breaking the user experience.

    Args:
        max_results: Maximum number of results to parse (-1 for all)

    Returns:
        List of dicts containing result data
    """
    # Ultra-simple semantic approach: just find external links and their text
    max_results_js = max_results if max_results > 0 else 10

    semantic_js = f'''
    var results = [];
    var allLinks = document.querySelectorAll('a[href]');
    var count = 0;
    for (var i = 0; i < allLinks.length && count < {max_results_js}; i++) {{
        var link = allLinks[i];
        var href = link.href || '';
        var text = (link.textContent || '').trim();
        if (href.indexOf('http') === 0 &&
            href.indexOf('google.com') === -1 &&
            text.length > 10 &&
            text.length < 150) {{
            results.push({{
                title: text,
                url: href,
                description: '',
                displayUrl: href.replace('https://', '').replace('http://', '').split('/')[0],
                position: count + 1
            }});
            count++;
        }}
    }}
    JSON.stringify(results);
    '''

    # Execute the semantic JavaScript
    js_escaped = semantic_js.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')

    applescript = f'''
    tell application "Safari"
        try
            set jsResult to do JavaScript "{js_escaped}" in current tab of window 1
            return jsResult
        on error errMsg
            return "ERROR: " & errMsg
        end try
    end tell
    '''

    try:
        result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)

        if result.returncode == 0:
            response = result.stdout.strip()
            if response.startswith('ERROR:'):
                logging.error(f"JavaScript execution error: {response}")
                return []

            # Parse JSON response
            try:
                parsed_results = json.loads(response)
                logging.debug(f"Successfully parsed {len(parsed_results)} results")
                return parsed_results
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse results JSON: {e}")
                logging.error(f"Raw response: {response[:200]}...")
                return []
        else:
            logging.error(f"AppleScript execution failed: {result.stderr}")
            return []

    except Exception as e:
        logging.error(f"Error parsing Google results: {e}")
        return []


def navigate_to_url(url: str, new_tab: bool = False):
    """Open URL in Chrome, optionally in a new tab that becomes active."""
    try:
        if new_tab:
            # Use AppleScript to create new tab and make it active
            script = f'''
            tell application "Google Chrome"
                activate
                if (count of windows) = 0 then
                    make new window
                    set URL of active tab of front window to "{url}"
                else
                    tell front window
                        make new tab
                        set URL of active tab to "{url}"
                    end tell
                end if
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"AppleScript error: {result.stderr}")
            print(f"✓ Opened in new Chrome tab: {url}")
        else:
            # Navigate in current tab
            script = f'''
            tell application "Google Chrome"
                activate
                if (count of windows) = 0 then
                    make new window
                end if
                set URL of active tab of front window to "{url}"
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"AppleScript error: {result.stderr}")
            print(f"✓ Opened in Chrome: {url}")

    except Exception as e:
        print(f"Error opening URL: {e}", file=sys.stderr)
        sys.exit(1)


def create_new_tab():
    """Create a new empty Safari tab."""
    try:
        subprocess.run(['open', '-a', 'Safari', 'about://'], check=True)
        print("✓ Created new Safari tab")
    except Exception as e:
        print(f"Error creating new tab: {e}", file=sys.stderr)
        sys.exit(1)


def open_url_in_new_tab(url: str):
    """Open URL in a new Safari tab and return focus to the original tab."""
    print(f"📑 Opening {url} in new tab...")

    try:
        # Create new tab, navigate to URL, then return focus to the original tab
        script = f'''
        tell application "Safari"
            activate

            -- Remember which tab was current before we start
            set originalTab to current tab of front window

            -- Create new tab at the end
            make new tab at end of tabs of front window

            -- Navigate the new tab to the URL
            set URL of last tab of front window to "{url}"

            -- Return focus to the original tab so subsequent operations don't affect the new tab
            set current tab of front window to originalTab

        end tell
        '''

        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Failed to open URL in new tab: {result.stderr}")

        print(f"✅ Opened {url} in new tab (focus returned to original tab)")

    except Exception as e:
        print(f"Error opening URL in new tab: {e}", file=sys.stderr)
        sys.exit(1)


def extract_page_content(url: str, output_path: str = None) -> dict:
    """Navigate to URL and extract page content as structured JSON."""
    print(f"🌐 Extracting content from: {url}")

    try:
        # Navigate to the URL - make sure we use the frontmost window
        script = f'''
        tell application "Safari"
            activate
            set URL of current tab of front window to "{url}"
        end tell
        '''

        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Failed to navigate to URL: {result.stderr}")

        print(f"✓ Navigation command sent to Safari")

        # Wait for page to load
        print(f"⏳ Waiting for page to load...")
        time.sleep(6)

        # Verify we're on the right page
        verify_script = 'tell application "Safari" to return URL of current tab of front window'
        verify_result = subprocess.run(['osascript', '-e', verify_script], capture_output=True, text=True)
        if verify_result.returncode == 0:
            current_url = verify_result.stdout.strip()
            print(f"📍 Current page: {current_url}")
        else:
            print("⚠️  Could not verify current page")

        # Much simpler JavaScript - start basic and build up
        extraction_js = '''
        var result = {
            url: window.location.href,
            title: document.title,
            text_content: [],
            headings: [],
            links: [],
            debug_info: {
                actual_url: window.location.href,
                hostname: window.location.hostname,
                pathname: window.location.pathname
            }
        };

        var paras = document.querySelectorAll('p');
        for (var i = 0; i < paras.length && i < 10; i++) {
            var text = paras[i].textContent.trim();
            if (text.length > 10) {
                result.text_content.push(text);
            }
        }

        var heads = document.querySelectorAll('h1, h2, h3');
        for (var i = 0; i < heads.length && i < 10; i++) {
            result.headings.push(heads[i].textContent.trim());
        }

        var links = document.querySelectorAll('a[href]');
        for (var i = 0; i < links.length && i < 10; i++) {
            var link = links[i];
            if (link.href.indexOf('http') === 0) {
                result.links.push({
                    text: link.textContent.trim(),
                    url: link.href
                });
            }
        }

        JSON.stringify(result);
        '''

        # Execute the JavaScript with proper escaping
        js_escaped = extraction_js.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')

        applescript = f'''
        tell application "Safari"
            try
                do JavaScript "{js_escaped}" in current tab of front window
            on error errMsg
                return "ERROR: " & errMsg
            end try
        end tell
        '''

        result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)

        if result.returncode == 0:
            response = result.stdout.strip()
            if response.startswith('ERROR:'):
                logging.error(f"JavaScript execution error: {response}")
                return {}

            # Parse JSON response
            try:
                page_data = json.loads(response)
                print(f"✅ Extracted content: {len(page_data.get('text_content', []))} text blocks, {len(page_data.get('links', []))} links, {len(page_data.get('headings', []))} headings")

                # Output results
                if output_path:
                    with open(output_path, 'w') as f:
                        json.dump(page_data, f, indent=2)
                    print(f"💾 Page content saved to: {output_path}")
                else:
                    print(json.dumps(page_data, indent=2))

                return page_data
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse page content JSON: {e}")
                logging.error(f"Raw response: {response[:200]}...")
                return {}
        else:
            logging.error(f"AppleScript execution failed: {result.stderr}")
            return {}

    except Exception as e:
        logging.error(f"Error extracting page content: {e}")
        return {}


def perform_jsearch(query: str, output_path: str = None) -> List[dict]:
    """Perform Google search and return structured JSON results."""
    print(f"🔍 Searching Google for: '{query}'")

    # URL encode the query for Google search
    encoded_query = urllib.parse.quote_plus(query)
    search_url = f"https://www.google.com/search?q={encoded_query}"

    try:
        # Navigate to search URL
        script = f'''
        tell application "Safari"
            set URL of current tab of window 1 to "{search_url}"
        end tell
        '''

        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Failed to navigate to search: {result.stderr}")

        # Wait for page to load
        time.sleep(3)

        # Use the same approach as the working search function
        extraction_js = f'''
        var results = [];
        var allLinks = document.querySelectorAll('a[href]');
        var count = 0;
        for (var i = 0; i < allLinks.length && count < 10; i++) {{
            var link = allLinks[i];
            var href = link.href || '';
            var text = (link.textContent || '').trim();
            if (href.indexOf('http') === 0 &&
                href.indexOf('google.com') === -1 &&
                text.length > 10 &&
                text.length < 150) {{
                results.push({{
                    title: text,
                    url: href,
                    snippet: 'Google search result',
                    displayUrl: href.replace('https://', '').replace('http://', '').split('/')[0],
                    position: count + 1
                }});
                count++;
            }}
        }}
        JSON.stringify(results);
        '''

        # Execute the JavaScript with proper escaping
        js_escaped = extraction_js.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')

        applescript = f'''
        tell application "Safari"
            try
                do JavaScript "{js_escaped}" in current tab of window 1
            on error errMsg
                return "ERROR: " & errMsg
            end try
        end tell
        '''

        result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)

        if result.returncode == 0:
            response = result.stdout.strip()
            if response.startswith('ERROR:'):
                logging.error(f"JavaScript execution error: {response}")
                return []

            # Parse JSON response
            try:
                parsed_results = json.loads(response)
                print(f"✅ Found {len(parsed_results)} search results")

                # Output results
                if output_path:
                    with open(output_path, 'w') as f:
                        json.dump(parsed_results, f, indent=2)
                    print(f"💾 Results saved to: {output_path}")
                else:
                    print(json.dumps(parsed_results, indent=2))

                return parsed_results
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse results JSON: {e}")
                logging.error(f"Raw response: {response[:200]}...")
                return []
        else:
            logging.error(f"AppleScript execution failed: {result.stderr}")
            return []

    except Exception as e:
        logging.error(f"Error performing jsearch: {e}")
        return []


def execute_box_command(command: str, session_name: str = "trot"):
    """Execute command in a named tmux session."""
    current_dir = os.getcwd()  # Get caller's current working directory

    try:
        # Check if box session exists
        check_result = subprocess.run(
            ['tmux', 'has-session', '-t', session_name],
            capture_output=True,
            text=True
        )

        # Create session if it doesn't exist
        if check_result.returncode != 0:
            print(f"📦 Creating new tmux session: {session_name}")
            create_result = subprocess.run(
                ['tmux', 'new-session', '-d', '-s', session_name],
                capture_output=True,
                text=True
            )

            if create_result.returncode != 0:
                raise Exception(f"Failed to create tmux session: {create_result.stderr}")

            # Small delay to ensure session is ready
            time.sleep(0.5)

        print(f"📦 Executing in box: {command}")

        # First, change to the caller's current working directory
        cd_result = subprocess.run(
            ['tmux', 'send-keys', '-t', session_name, f'cd "{current_dir}"', 'Enter'],
            capture_output=True,
            text=True
        )

        if cd_result.returncode != 0:
            raise Exception(f"Failed to change directory in session: {cd_result.stderr}")

        # Small delay to ensure cd completes
        time.sleep(0.2)

        # Send the actual command to the session
        send_result = subprocess.run(
            ['tmux', 'send-keys', '-t', session_name, command, 'Enter'],
            capture_output=True,
            text=True
        )

        if send_result.returncode != 0:
            raise Exception(f"Failed to send command to session: {send_result.stderr}")

        print(f"✅ Command sent to box")

    except Exception as e:
        print(f"Error executing box command: {e}", file=sys.stderr)
        sys.exit(1)


def get_box_output(lines: int = 50, session_name: str = "trot"):
    """Get the last N lines from a named tmux session."""

    try:
        # Check if box session exists
        check_result = subprocess.run(
            ['tmux', 'has-session', '-t', session_name],
            capture_output=True,
            text=True
        )

        if check_result.returncode != 0:
            print(f"Error: No box session exists. Run 'ctrl box <command>' first.", file=sys.stderr)
            sys.exit(1)

        # Capture the pane content
        capture_result = subprocess.run(
            ['tmux', 'capture-pane', '-t', session_name, '-p', '-S', f'-{lines}'],
            capture_output=True,
            text=True
        )

        if capture_result.returncode != 0:
            raise Exception(f"Failed to capture box output: {capture_result.stderr}")

        print(capture_result.stdout)

    except Exception as e:
        print(f"Error getting box output: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_search(args):
    """Handle the search command."""
    if not args.query:
        print("Error: No search query provided", file=sys.stderr)
        sys.exit(1)

    query = ' '.join(args.query)
    new_tab = getattr(args, 'new_tab', False)
    parse_results = hasattr(args, 'results') and args.results is not None
    max_results = getattr(args, 'results', None) if parse_results else None
    output_json = getattr(args, 'json', False)

    if parse_results:
        print(f"🔍 Searching for '{query}' and parsing results...")
        search_results = search_google(query, max_results, new_tab)

        if search_results:
            if output_json:
                print(json.dumps(search_results, indent=2))
            else:
                print(f"Found {len(search_results)} results:\n")
                for i, result in enumerate(search_results, 1):
                    print(f"{i}. {result['title']}")
                    print(f"   URL: {result['url']}")
                    if result['description']:
                        print(f"   Description: {result['description']}")
                    print()
        else:
            print("No search results found or failed to parse results.")
    else:
        if new_tab:
            print(f"🔍 Opening search for '{query}' in new Safari tab...")
        else:
            print(f"🔍 Searching for '{query}' in Safari...")

        search_google(query, None, new_tab)
        print(f"✓ Search completed")


def cmd_navigate(args):
    """Handle the navigate command."""
    if not args.url:
        print("Error: No URL provided", file=sys.stderr)
        sys.exit(1)

    url = args.url[0] if isinstance(args.url, list) else args.url
    new_tab = getattr(args, 'new_tab', False)

    navigate_to_url(url, new_tab)


def cmd_new_tab(args):
    """Handle the new-tab command."""
    create_new_tab()


def cmd_box(args):
    """Handle the box command - execute command in a named tmux session."""
    if not args.box_command:
        print("Error: No command provided", file=sys.stderr)
        sys.exit(1)

    session_name = getattr(args, 'session_name', 'trot')
    command = ' '.join(args.box_command)
    execute_box_command(command, session_name)


def cmd_outbox(args):
    """Handle the outbox command - get output from a named tmux session."""
    session_name = getattr(args, 'session_name', 'trot')
    lines = args.lines if args.lines else 50
    get_box_output(lines, session_name)


def cmd_jsearch(args):
    """Handle the jsearch command."""
    if not args.query:
        print("Error: No search query provided", file=sys.stderr)
        sys.exit(1)

    perform_jsearch(args.query, args.output)


def cmd_jpage(args):
    """Handle the jpage command."""
    if not args.url:
        print("Error: No URL provided", file=sys.stderr)
        sys.exit(1)

    # Ensure URL has protocol
    url = args.url
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    extract_page_content(url, args.output)


def cmd_tab(args):
    """Handle the tab command."""
    if not args.url:
        print("Error: No URL provided", file=sys.stderr)
        sys.exit(1)

    # Ensure URL has protocol
    url = args.url
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    open_url_in_new_tab(url)


def extract_list_from_page(output_path: str = None, min_items: int = 3) -> List[dict]:
    """
    Extract a repeating list structure from the current Safari page.

    This function uses heuristics to find repeated patterns in the DOM:
    - Looks for containers with multiple similar child elements
    - Identifies visual hierarchy (larger fonts = titles/headings)
    - Extracts structured data into dictionaries

    Args:
        output_path: Optional file path to save JSON output
        min_items: Minimum number of repeated items to consider a valid list (default: 3)

    Returns:
        List of dicts containing extracted list items
    """
    print(f"🔍 Analyzing page structure for repeating lists...")

    # JavaScript - simplified and more compact version with style metadata
    extraction_js = '''var r=[];var a=document.querySelectorAll('*');for(var i=0;i<a.length;i++){var e=a[i];var c=Array.from(e.children).filter(function(x){var s=getComputedStyle(x);return s.display!=='none'&&s.visibility!=='hidden';});if(c.length>=''' + str(min_items) + '''){var t={};c.forEach(function(x){t[x.tagName]=(t[x.tagName]||0)+1;});var mt='',mc=0;for(var k in t){if(t[k]>mc){mc=t[k];mt=k;}}if(mc/c.length>=0.6){r.push({e:e,c:c.filter(function(x){return x.tagName===mt;}),s:mc/c.length,n:mc});}}}r.sort(function(a,b){return(b.s*Math.log(b.n+1))-(a.s*Math.log(a.n+1));});if(r.length===0){JSON.stringify({success:false,error:'No list found',items:[]});}else{var b=r[0];var items=[];b.c.forEach(function(item,idx){var fields={};var descendants=item.querySelectorAll('*');var texts=[];for(var j=0;j<descendants.length;j++){var d=descendants[j];var txt=d.textContent.trim();if(txt.length>0&&txt.length<300){var style=getComputedStyle(d);var fs=Math.round(parseFloat(style.fontSize));var color=style.color;var rgb=color.match(/rgb\\((\\d+),\\s*(\\d+),\\s*(\\d+)\\)/);var hexColor='';if(rgb){var r=parseInt(rgb[1]);var g=parseInt(rgb[2]);var b=parseInt(rgb[3]);hexColor=((r<<16)|(g<<8)|b).toString(16).padStart(6,'0');}var isBlack=(hexColor==='000000'||hexColor==='');var suffix=' ~:~ s'+fs;if(!isBlack&&hexColor){suffix+=' c'+hexColor;}texts.push({t:txt+suffix,f:fs,tag:d.tagName.toLowerCase()});}}texts.sort(function(a,b){return b.f-a.f;});texts.forEach(function(x,i){var fn=i===0?'title':i===1?'subtitle':i===2?'description':'field_'+(i+1);fields[fn]=x.t;});items.push(Object.assign({position:idx+1},fields));});JSON.stringify({success:true,url:location.href,itemCount:items.length,items:items,metadata:{containerTag:b.e.tagName,itemTag:b.c[0].tagName,similarity:b.s}});}'''

    # Execute the JavaScript with proper escaping
    js_escaped = extraction_js.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')

    applescript = f'''
    tell application "Safari"
        try
            do JavaScript "{js_escaped}" in current tab of window 1
        on error errMsg
            return "ERROR: " & errMsg
        end try
    end tell
    '''

    try:
        result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            response = result.stdout.strip()

            # Debug: show what we got
            if not response:
                print(f"❌ Error: JavaScript returned empty response")
                logging.error("JavaScript returned empty response")
                return []

            if response.startswith('ERROR:'):
                logging.error(f"JavaScript execution error: {response}")
                print(f"❌ Error: {response}")
                return []

            # Parse JSON response
            try:
                data = json.loads(response)

                if not data.get('success', False):
                    print(f"❌ {data.get('error', 'Unknown error')}")
                    return []

                items = data.get('items', [])
                metadata = data.get('metadata', {})

                print(f"✅ Found {len(items)} list items")
                print(f"📦 Container: <{metadata.get('containerTag', 'unknown').lower()}>")
                print(f"📄 Item type: <{metadata.get('itemTag', 'unknown').lower()}>")
                print(f"🎯 Similarity: {metadata.get('similarity', 0):.1%}")

                # Output results
                if output_path:
                    with open(output_path, 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"💾 Results saved to: {output_path}")
                else:
                    print("\n" + json.dumps(data, indent=2))

                return items

            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse results JSON: {e}")
                logging.error(f"Raw response: {response[:200]}...")
                print(f"❌ Failed to parse results")
                return []
        else:
            logging.error(f"AppleScript execution failed: {result.stderr}")
            print(f"❌ AppleScript failed: {result.stderr}")
            return []

    except Exception as e:
        logging.error(f"Error extracting list from page: {e}")
        print(f"❌ Error: {e}")
        return []


def cmd_jgetlist(args):
    """Handle the jgetlist command."""
    min_items = getattr(args, 'min_items', 3)
    output = getattr(args, 'output', None)
    extract_list_from_page(output, min_items)


# ============================================================================
# Playwright-based Advanced Commands
# ============================================================================

def get_current_safari_url() -> str:
    """Get the current URL from Safari's active tab."""
    script = 'tell application "Safari" to return URL of current tab of front window'
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def extract_page_with_playwright(url: str = None, output_path: str = None) -> dict:
    """
    Extract page content using Playwright for advanced DOM access.

    Args:
        url: URL to extract from, or None to use current Safari page (indicated by '-')
        output_path: Optional file path to save JSON output

    Returns:
        Dict containing page structure with full DOM access
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ Error: Playwright not installed.")
        print("   Install with: pip install playwright && playwright install")
        sys.exit(1)

    # If no URL provided or '-', get current Safari URL
    if url is None or url == '-':
        print("📍 Getting current Safari page URL...")
        url = get_current_safari_url()
        if not url:
            print("❌ Error: Could not get current Safari URL")
            sys.exit(1)
        print(f"🌐 Extracting from: {url}")
    else:
        print(f"🌐 Navigating to: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, wait_until='networkidle', timeout=30000)

            # Extract comprehensive page data
            page_data = page.evaluate('''() => {
                return {
                    url: window.location.href,
                    title: document.title,
                    html: document.documentElement.outerHTML,
                    text: document.body.innerText,
                    metadata: {
                        description: document.querySelector('meta[name="description"]')?.content || '',
                        keywords: document.querySelector('meta[name="keywords"]')?.content || '',
                        ogTitle: document.querySelector('meta[property="og:title"]')?.content || '',
                        ogDescription: document.querySelector('meta[property="og:description"]')?.content || ''
                    },
                    headings: {
                        h1: Array.from(document.querySelectorAll('h1')).map(h => h.textContent.trim()),
                        h2: Array.from(document.querySelectorAll('h2')).map(h => h.textContent.trim()),
                        h3: Array.from(document.querySelectorAll('h3')).map(h => h.textContent.trim())
                    },
                    links: Array.from(document.querySelectorAll('a[href]')).map(a => ({
                        text: a.textContent.trim(),
                        href: a.href
                    })).slice(0, 50),
                    images: Array.from(document.querySelectorAll('img[src]')).map(img => ({
                        src: img.src,
                        alt: img.alt || ''
                    })).slice(0, 20)
                };
            }''')

            print(f"✅ Extracted page data successfully")
            print(f"   Title: {page_data.get('title', 'N/A')}")
            print(f"   Headings: {len(page_data.get('headings', {}).get('h1', []))} H1, {len(page_data.get('headings', {}).get('h2', []))} H2")
            print(f"   Links: {len(page_data.get('links', []))}")
            print(f"   Images: {len(page_data.get('images', []))}")

            # Output results
            if output_path:
                with open(output_path, 'w') as f:
                    json.dump(page_data, f, indent=2)
                print(f"💾 Results saved to: {output_path}")
            else:
                print("\n" + json.dumps(page_data, indent=2))

            return page_data

        finally:
            browser.close()


def cmd_jjpage(args):
    """Handle the jjpage command (Playwright version)."""
    url = args.url if args.url != '-' else None
    output = getattr(args, 'output', None)
    extract_page_with_playwright(url, output)


# ============================================================================
# Chrome DevTools Protocol (CDP) - Building Blocks
# ============================================================================

def check_chrome_debug_port(port: int = 9222) -> bool:
    """
    Check if Chrome is running with remote debugging enabled.

    Args:
        port: CDP port number (default: 9222)

    Returns:
        True if Chrome CDP is available, False otherwise
    """
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except Exception:
        return False


def launch_chrome_debug(port: int = 9222) -> subprocess.Popen:
    """
    Launch Chrome with remote debugging enabled.

    Args:
        port: CDP port number (default: 9222)

    Returns:
        Subprocess handle for Chrome process
    """
    chrome_paths = [
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Chromium.app/Contents/MacOS/Chromium',
    ]

    chrome_path = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_path = path
            break

    if not chrome_path:
        raise Exception("Chrome not found. Please install Google Chrome.")

    print(f"🚀 Launching Chrome with remote debugging on port {port}...")

    # Create temp directory for Chrome user data
    import tempfile
    user_data_dir = tempfile.mkdtemp(prefix='ctrl-chrome-')

    # Launch Chrome with remote debugging
    process = subprocess.Popen([
        chrome_path,
        f'--remote-debugging-port={port}',
        f'--user-data-dir={user_data_dir}',
        '--no-first-run',
        '--no-default-browser-check',
    ])

    # Wait for Chrome to be ready
    time.sleep(3)

    return process


def connect_to_chrome(port: int = 9222):
    """
    Connect Playwright to Chrome via CDP.

    Args:
        port: CDP port number (default: 9222)

    Returns:
        Playwright browser instance connected to Chrome
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ Error: Playwright not installed.")
        print("   Install with: pip install playwright && playwright install")
        sys.exit(1)

    playwright = sync_playwright().start()

    try:
        browser = playwright.chromium.connect_over_cdp(f"http://localhost:{port}")
        return playwright, browser
    except Exception as e:
        print(f"❌ Error connecting to Chrome: {e}")
        print(f"   Make sure Chrome is running with --remote-debugging-port={port}")
        sys.exit(1)


def get_chrome_tab_by_number(browser, tab_number: int):
    """
    Get a specific Chrome tab by its number.

    Args:
        browser: Playwright browser instance connected to Chrome
        tab_number: Tab index (1-based for positive, -1 for last, -2 for second-to-last, etc.)

    Returns:
        Selected page/tab
    """
    contexts = browser.contexts
    if not contexts:
        raise Exception("No browser contexts found")

    # Get the default context
    context = contexts[0]
    pages = context.pages

    if not pages:
        raise Exception("No tabs open in Chrome")

    print(f"🔍 Found {len(pages)} open tabs in Chrome")

    # List all tabs
    for i, page in enumerate(pages):
        url = page.url
        title_text = page.title() if hasattr(page, 'title') else 'Unknown'
        print(f"   Tab {i+1}: {title_text[:50]}")
        print(f"           {url[:70]}...")

    # Convert tab number to array index
    if tab_number > 0:
        # Positive numbers: 1-based indexing
        array_index = tab_number - 1
        if array_index >= len(pages):
            raise Exception(f"Tab {tab_number} does not exist (only {len(pages)} tabs open)")
    else:
        # Negative numbers: -1 is last, -2 is second-to-last, etc.
        array_index = tab_number
        if abs(tab_number) > len(pages):
            raise Exception(f"Tab {tab_number} does not exist (only {len(pages)} tabs open)")

    selected_page = pages[array_index]
    selected_title = selected_page.title() if hasattr(selected_page, 'title') else 'Unknown'

    # Calculate display number (1-based positive)
    display_number = array_index + 1 if array_index >= 0 else len(pages) + array_index + 1

    print(f"\n✅ Selected tab {display_number}: {selected_title[:50]}")
    print(f"   {selected_page.url[:70]}...")

    return selected_page


def extract_page_with_chrome(url: str = None, output_path: str = None, port: int = 9222, output_format: str = 'json', include_html: bool = False, font_filter = None, silent: bool = False) -> dict:
    """
    Extract page content using Chrome via CDP.

    Args:
        url: URL to navigate to, or None to use current tab (indicated by '-')
        output_path: Optional file path to save output
        port: CDP port number (default: 9222)
        output_format: Output format - 'json' or 'yaml' (default: 'json')
        include_html: Include full HTML in output (default: False)
        font_filter: Font format/filter - None for default f# prefix, '-' for legacy " ~:~ " suffix, integer N to filter and show only f1-fN
        silent: If True, suppress stdout output (default: False)

    Returns:
        Dict containing page structure with recursive text tree
    """
    # Check if Chrome debug is running
    chrome_running = check_chrome_debug_port(port)
    chrome_process = None

    if not chrome_running:
        chrome_process = launch_chrome_debug(port)
        chrome_running = True

    # Connect to Chrome
    playwright, browser = connect_to_chrome(port)

    try:
        # Parse the url parameter - it could be a tab number, URL, or '-'
        page = None

        is_existing_tab = True

        if url is None or url == '-':
            # '-' or None means last tab (-1)
            tab_number = -1
            page = get_chrome_tab_by_number(browser, tab_number)
            url = page.url
            print(f"🌐 Current page: {url}")
        elif url.startswith('http://') or url.startswith('https://'):
            # It's a URL - open in new tab
            print(f"🌐 Opening new tab: {url}")
            context = browser.contexts[0]
            page = context.new_page()
            page.goto(url, wait_until='domcontentloaded', timeout=15000)
            # Give it a moment to load dynamic content
            page.wait_for_timeout(2000)
            is_existing_tab = False
        else:
            # Try to parse as tab number
            try:
                tab_number = int(url)
                page = get_chrome_tab_by_number(browser, tab_number)
                url = page.url
                print(f"🌐 Current page: {url}")
            except ValueError:
                raise Exception(f"Invalid argument '{url}': must be a tab number (1, 2, -1, -2, etc.) or URL (http://... or https://...)")
            except Exception as e:
                raise e

        # For existing tabs, ensure all lazy-loaded content is visible
        if is_existing_tab:
            print("⏳ Scrolling to load all dynamic content...")
            # Scroll down in increments to trigger lazy loading
            page.evaluate('''() => {
                return new Promise((resolve) => {
                    let totalHeight = 0;
                    const distance = 500;
                    const timer = setInterval(() => {
                        window.scrollBy(0, distance);
                        totalHeight += distance;

                        if (totalHeight >= document.body.scrollHeight) {
                            clearInterval(timer);
                            // Scroll back to top
                            window.scrollTo(0, 0);
                            setTimeout(resolve, 1000);
                        }
                    }, 200);
                });
            }''')
            print("✅ Dynamic content loaded")

        # Extract comprehensive page data with recursive text tree
        # Process font_filter parameter
        use_legacy = False
        max_font_number = None

        if font_filter == '-':
            # Legacy format mode
            use_legacy = True
        elif font_filter is not None:
            # Try to parse as integer for filtering mode
            try:
                max_font_number = int(font_filter)
            except (ValueError, TypeError):
                # If not parseable as int, treat as legacy
                use_legacy = True

        use_legacy_js = 'true' if use_legacy else 'false'
        max_font_js = str(max_font_number) if max_font_number is not None else 'null'

        page_data = page.evaluate(f'''() => {{
            const USE_LEGACY_FORMAT = {use_legacy_js};
            const MAX_FONT_NUMBER = {max_font_js};

            // Font annotation and filtering function - adds font markup to text and filters based on font rank
            // Returns null if text should be filtered out
            function fontAnnotation(text, node, fontMap) {{
                const style = getComputedStyle(node);
                const fontSize = Math.round(parseFloat(style.fontSize));
                const color = style.color;
                const fontWeight = style.fontWeight;
                const fontStyle = style.fontStyle;

                // Convert RGB color to hex
                let hexColor = '';
                const rgbMatch = color.match(/rgb\\((\\d+),\\s*(\\d+),\\s*(\\d+)\\)/);
                if (rgbMatch) {{
                    const r = parseInt(rgbMatch[1]);
                    const g = parseInt(rgbMatch[2]);
                    const b = parseInt(rgbMatch[3]);
                    hexColor = ((r << 16) | (g << 8) | b).toString(16).padStart(6, '0');
                }}

                if (USE_LEGACY_FORMAT) {{
                    // Legacy format: " ~:~ s## c######"
                    const isBlack = (hexColor === '000000' || hexColor === '');
                    let suffix = ' ~:~ s' + fontSize;
                    if (!isBlack && hexColor) {{
                        suffix += ' c' + hexColor;
                    }}
                    return text + suffix;
                }} else {{
                    // New format: "f# " prefix
                    const fontKey = fontSize + '|' + hexColor + '|' + fontWeight + '|' + fontStyle;
                    const fontName = fontMap.get(fontKey) || 'f0';

                    // Apply filtering if MAX_FONT_NUMBER is set
                    if (MAX_FONT_NUMBER !== null) {{
                        // Extract font number from fontName (e.g., "f3" -> 3)
                        const fontNumber = parseInt(fontName.substring(1));
                        if (fontNumber > MAX_FONT_NUMBER) {{
                            return null; // Filter out this text
                        }}
                    }}

                    return fontName + ' ' + text;
                }}
            }}

            // Collect all unique fonts on the page and rank them
            function collectAndRankFonts() {{
                const fontSet = new Map(); // fontKey -> {{size, color, weight, style, count}}

                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_ELEMENT,
                    {{
                        acceptNode: function(node) {{
                            const text = Array.from(node.childNodes)
                                .filter(n => n.nodeType === Node.TEXT_NODE)
                                .map(n => n.textContent.trim())
                                .join(' ')
                                .trim();
                            return text.length > 0 ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP;
                        }}
                    }}
                );

                let node;
                while (node = walker.nextNode()) {{
                    const style = getComputedStyle(node);
                    const fontSize = Math.round(parseFloat(style.fontSize));
                    const color = style.color;
                    const fontWeight = style.fontWeight;
                    const fontStyle = style.fontStyle;

                    // Convert RGB to hex
                    let hexColor = '';
                    const rgbMatch = color.match(/rgb\\((\\d+),\\s*(\\d+),\\s*(\\d+)\\)/);
                    if (rgbMatch) {{
                        const r = parseInt(rgbMatch[1]);
                        const g = parseInt(rgbMatch[2]);
                        const b = parseInt(rgbMatch[3]);
                        hexColor = ((r << 16) | (g << 8) | b).toString(16).padStart(6, '0');
                    }}

                    const fontKey = fontSize + '|' + hexColor + '|' + fontWeight + '|' + fontStyle;

                    if (!fontSet.has(fontKey)) {{
                        fontSet.set(fontKey, {{
                            size: fontSize,
                            color: hexColor,
                            weight: fontWeight,
                            style: fontStyle,
                            count: 1
                        }});
                    }} else {{
                        fontSet.get(fontKey).count++;
                    }}
                }}

                // Convert to array and sort by emphasis
                const fonts = Array.from(fontSet.entries()).map(([key, data]) => ({{
                    key: key,
                    ...data
                }}));

                // Sort by: 1) size (larger first), 2) darkness (darker first), 3) weight (bolder first)
                fonts.sort((a, b) => {{
                    // Primary: size (descending)
                    if (a.size !== b.size) return b.size - a.size;

                    // Secondary: darkness (lower hex value = darker, but handle black specially)
                    const aDarkness = a.color === '000000' ? 0 : parseInt(a.color, 16);
                    const bDarkness = b.color === '000000' ? 0 : parseInt(b.color, 16);
                    if (aDarkness !== bDarkness) return aDarkness - bDarkness;

                    // Tertiary: weight (higher = bolder)
                    const aWeight = parseInt(a.weight) || 400;
                    const bWeight = parseInt(b.weight) || 400;
                    if (aWeight !== bWeight) return bWeight - aWeight;

                    // Quaternary: italic vs normal (italic comes after)
                    if (a.style !== b.style) {{
                        return a.style === 'italic' ? 1 : -1;
                    }}

                    return 0;
                }});

                // Create font map: fontKey -> fontName (f1, f2, f3, etc.)
                const fontMap = new Map();
                const fontSpecs = {{}};
                fonts.forEach((font, index) => {{
                    const fontName = 'f' + (index + 1);
                    fontMap.set(font.key, fontName);

                    // Store font specification
                    fontSpecs[fontName] = {{
                        size: font.size,
                        color: font.color,
                        weight: font.weight,
                        style: font.style,
                        count: font.count
                    }};
                }});

                return {{fontMap, fontSpecs}};
            }}

            // Detect if an element should have a separator after it
            // Returns: null (no separator), 'thin' (thin divider line), or 'container' (border on content container)
            function checkForSeparator(node) {{
                // Must be a structural element (not text, button, input, etc.)
                const structuralTags = ['DIV', 'HR', 'SECTION', 'ARTICLE'];
                if (!structuralTags.includes(node.tagName)) {{
                    return null;
                }}

                // HR tags are always separators
                if (node.tagName === 'HR') {{
                    return 'thin';
                }}

                const style = getComputedStyle(node);
                const rect = node.getBoundingClientRect();

                // Check for visible border-bottom (most common for card separators)
                const borderBottomWidth = parseFloat(style.borderBottomWidth);
                if (borderBottomWidth < 1) {{
                    return null;
                }}

                // Check if element is wide enough to be a visual separator
                if (rect.width < 400) {{
                    return null;
                }}

                const textContent = node.textContent.trim();

                // Thin separator: minimal text, small height
                if (textContent.length <= 10 && rect.height <= 30) {{
                    return 'thin';
                }}

                // Container with bottom border: has content, reasonable height
                // These are things like provider cards, article cards, etc.
                if (textContent.length > 50 && rect.height > 100 && rect.height < 600) {{
                    // Additional check: should span significant width
                    const parentRect = node.parentElement?.getBoundingClientRect();
                    if (parentRect && rect.width / parentRect.width >= 0.7) {{
                        return 'container';
                    }}
                }}

                return null;
            }}

            // Build recursive text tree based on heading hierarchy
            function buildTextTree(fontMap) {{
                const result = [];
                const stack = [{{level: 0, array: result}}];
                const seenSeparators = new Set(); // Track containers that have had separators added
                const containerStack = [];  // Track container elements we're inside

                // Get all elements in body that are headings or have text content
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_ELEMENT,
                    {{
                        acceptNode: function(node) {{
                            // Accept headings
                            if (/^H[1-6]$/i.test(node.tagName)) {{
                                return NodeFilter.FILTER_ACCEPT;
                            }}
                            // Accept elements with direct text content
                            const text = Array.from(node.childNodes)
                                .filter(n => n.nodeType === Node.TEXT_NODE)
                                .map(n => n.textContent.trim())
                                .join(' ')
                                .trim();
                            if (text.length > 0) {{
                                return NodeFilter.FILTER_ACCEPT;
                            }}
                            return NodeFilter.FILTER_SKIP;
                        }}
                    }}
                );

                let node;
                let lastProcessedContainer = null;

                while (node = walker.nextNode()) {{
                    const tagName = node.tagName;

                    // Check if current node is a thin separator
                    const sepType = checkForSeparator(node);
                    if (sepType === 'thin') {{
                        if (!seenSeparators.has(node)) {{
                            seenSeparators.add(node);
                            stack[stack.length - 1].array.push('~ ~ ~ ~ ~ ~ ~ ~ ~');
                        }}
                        continue;
                    }}

                    // Find nearest ancestor that is a separator container
                    // (Container DIVs don't have direct text, so walker doesn't visit them)
                    let containerAncestor = null;
                    let parent = node.parentElement;
                    while (parent && parent !== document.body) {{
                        const parentSepType = checkForSeparator(parent);
                        if (parentSepType === 'container') {{
                            containerAncestor = parent;
                            break;
                        }}
                        parent = parent.parentElement;
                    }}

                    // If we found a container ancestor and it's different from the last one, add separator
                    if (containerAncestor && lastProcessedContainer && containerAncestor !== lastProcessedContainer) {{
                        if (!seenSeparators.has(lastProcessedContainer)) {{
                            seenSeparators.add(lastProcessedContainer);
                            stack[stack.length - 1].array.push('~ ~ ~ ~ ~ ~ ~ ~ ~');
                        }}
                    }}

                    // Update last processed container
                    if (containerAncestor) {{
                        lastProcessedContainer = containerAncestor;
                    }}

                    // Handle headings
                    if (/^H[1-6]$/i.test(tagName)) {{
                        const level = parseInt(tagName.substring(1));
                        const text = node.textContent.trim();
                        if (!text) continue;

                        // Pop stack to appropriate level
                        while (stack.length > 1 && stack[stack.length - 1].level >= level) {{
                            stack.pop();
                        }}

                        // Create new sublist for this heading
                        const newList = [tagName + ' ' + text];
                        stack[stack.length - 1].array.push(newList);

                        // Push this level onto stack
                        stack.push({{level: level, array: newList}});
                    }} else {{
                        // Handle text content (non-heading elements)
                        const text = Array.from(node.childNodes)
                            .filter(n => n.nodeType === Node.TEXT_NODE)
                            .map(n => n.textContent.trim())
                            .filter(t => t.length > 0)
                            .join(' ')
                            .trim();

                        if (text && text.length > 0) {{
                            const annotatedText = fontAnnotation(text, node, fontMap);
                            // Only add text if it wasn't filtered out (fontAnnotation returns null for filtered text)
                            if (annotatedText !== null) {{
                                stack[stack.length - 1].array.push(annotatedText);
                            }}
                        }}
                    }}
                }}

                // Add separator after the last container if needed
                if (lastProcessedContainer && !seenSeparators.has(lastProcessedContainer)) {{
                    stack[stack.length - 1].array.push('~ ~ ~ ~ ~ ~ ~ ~ ~');
                }}

                return result;
            }}

            // Main execution
            let fontMap = new Map();
            let fontSpecs = {{}};

            if (!USE_LEGACY_FORMAT) {{
                const fontData = collectAndRankFonts();
                fontMap = fontData.fontMap;
                fontSpecs = fontData.fontSpecs;
            }}

            const result = {{
                url: window.location.href,
                title: document.title,
                metadata: {{
                    description: document.querySelector('meta[name="description"]')?.content || '',
                    keywords: document.querySelector('meta[name="keywords"]')?.content || '',
                    ogTitle: document.querySelector('meta[property="og:title"]')?.content || '',
                    ogDescription: document.querySelector('meta[property="og:description"]')?.content || ''
                }},
                headings: {{
                    h1: Array.from(document.querySelectorAll('h1')).map(h => h.textContent.trim()),
                    h2: Array.from(document.querySelectorAll('h2')).map(h => h.textContent.trim()),
                    h3: Array.from(document.querySelectorAll('h3')).map(h => h.textContent.trim())
                }}
            }};

            // Add fonts section only when not using legacy format
            if (!USE_LEGACY_FORMAT) {{
                result.fonts = fontSpecs;
            }}

            // Add text section
            result.text = buildTextTree(fontMap);

            // Add links and images
            result.links = Array.from(document.querySelectorAll('a[href]')).map(a => ({{
                text: a.textContent.trim(),
                href: a.href
            }})).slice(0, 50);
            result.images = Array.from(document.querySelectorAll('img[src]')).map(img => ({{
                src: img.src,
                alt: img.alt || ''
            }})).slice(0, 20);

            return result;
        }}''')

        # Add HTML if requested
        if include_html:
            html_content = page.evaluate('() => document.documentElement.outerHTML')
            page_data['html'] = html_content

        if not silent:
            print(f"✅ Extracted page data successfully")
            print(f"   Title: {page_data.get('title', 'N/A')}")
            print(f"   Headings: {len(page_data.get('headings', {}).get('h1', []))} H1, {len(page_data.get('headings', {}).get('h2', []))} H2")
            print(f"   Text tree depth: {len(page_data.get('text', []))} top-level items")
            print(f"   Links: {len(page_data.get('links', []))}")
            print(f"   Images: {len(page_data.get('images', []))}")
            if include_html:
                print(f"   HTML: {len(page_data.get('html', '')):,} characters")

        # Output results
        if not silent and output_format == 'yaml' and not YAML_AVAILABLE:
            print("❌ Error: YAML output requested but PyYAML is not installed.")
            print("   Install with: pip install pyyaml")
            sys.exit(1)

        if output_path:
            with open(output_path, 'w') as f:
                if output_format == 'yaml':
                    yaml.dump(page_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                else:
                    json.dump(page_data, f, indent=2)
            if not silent:
                print(f"💾 Results saved to: {output_path} ({output_format.upper()} format)")
        elif not silent:
            if output_format == 'yaml':
                print("\n" + yaml.dump(page_data, default_flow_style=False, allow_unicode=True, sort_keys=False))
            else:
                print("\n" + json.dumps(page_data, indent=2))

        return page_data

    finally:
        playwright.stop()


def extract_list_from_chrome(url: str = None, min: int = 5, port: int = 9222, font_filter = None) -> List[dict]:
    """
    Extract a list structure from a Chrome page by finding the most common font.

    Args:
        url: URL to navigate to, or None to use current tab (indicated by '-')
        min: Minimum count for a font to be considered a list item name (default: 5)
        port: CDP port number (default: 9222)
        font_filter: Font format/filter - None for default f# prefix, '-' for legacy " ~:~ " suffix, integer N to filter and show only f1-fN

    Returns:
        List of dicts representing extracted list items
    """
    # Get the full page data structure (silently, without printing to stdout)
    page_data = extract_page_with_chrome(url, output_path=None, port=port, output_format='json', include_html=False, font_filter=font_filter, silent=True)

    if not page_data or 'fonts' not in page_data:
        print("❌ Error: Could not extract page data or no fonts found")
        return []

    # Find the lowest f-number with count >= min
    fonts = page_data.get('fonts', {})
    target_font = None

    # Sort fonts by f-number (f1, f2, f3, ...)
    sorted_fonts = sorted(fonts.items(), key=lambda x: int(x[0][1:]))  # Extract number from "f3"

    for font_name, font_spec in sorted_fonts:
        if font_spec.get('count', 0) >= min:
            target_font = font_name
            print(f"📌 Using {font_name} as list item name (count: {font_spec['count']})")
            print(f"   Font spec: size={font_spec['size']}px, color=#{font_spec['color']}, weight={font_spec['weight']}")
            break

    if not target_font:
        print(f"❌ Error: No font found with count >= {min}")
        return []

    def looks_like_javascript(value: str) -> bool:
        """
        Check if a value looks like JavaScript code.

        Args:
            value: String to check

        Returns:
            True if the value appears to contain JavaScript, False otherwise
        """
        if not value or len(value) < 10:
            return False

        # JavaScript keywords and patterns
        js_keywords = [
            'function(', 'function ', '=>',
            'var ', 'let ', 'const ',
            'return ', 'if(', 'if ',
            'window.', 'document.',
            '{};', '()=>',
            '.prototype', '.addEventListener',
            'console.log', 'typeof ',
        ]

        # Check for JS patterns
        value_lower = value.lower()
        for keyword in js_keywords:
            if keyword.lower() in value_lower:
                return True

        # Check for multiple curly braces (common in JS)
        if value.count('{') > 1 or value.count('}') > 1:
            return True

        return False

    # Recursively traverse the text structure and extract list items
    def traverse_and_extract(node, current_item=None, items=None):
        """Recursively traverse the text tree and extract list items."""
        if items is None:
            items = []

        if isinstance(node, str):
            # Check if this string starts with our target font
            if node.startswith(target_font + ' '):
                # This is a new list item
                if current_item is not None:
                    # Save the previous item
                    items.append(current_item)

                # Start a new item
                text = node[len(target_font) + 1:]  # Strip "f3 " prefix
                current_item = {target_font: text}

            elif current_item is not None:
                # This is additional data for the current item
                # Extract the font number if present
                parts = node.split(' ', 1)
                if len(parts) == 2 and parts[0].startswith('f'):
                    font_key = parts[0]
                    font_value = parts[1]

                    # Filter out JavaScript-looking values
                    if looks_like_javascript(font_value):
                        return current_item

                    # Handle duplicate keys by concatenating with "; "
                    if font_key in current_item:
                        # Append to existing value with "; " separator
                        current_item[font_key] += '; ' + font_value
                    else:
                        # First occurrence - store as string
                        current_item[font_key] = font_value

        elif isinstance(node, list):
            # Recursively process list items
            for item in node:
                current_item = traverse_and_extract(item, current_item, items)

        return current_item

    text_tree = page_data.get('text', [])
    items = []
    last_item = traverse_and_extract(text_tree, None, items)

    # Don't forget to add the last item
    if last_item is not None:
        items.append(last_item)

    print(f"✅ Extracted {len(items)} list items")
    return items


def upload_file_to_chrome(file_path: str, url: str = None, selector: str = 'input[type="file"]', port: int = 9222):
    """
    Upload a file to the current Chrome page by setting the file input.

    Args:
        file_path: Path to the file to upload
        url: Optional URL to navigate to first, or None to use current tab
        selector: CSS selector for the file input element (default: 'input[type="file"]')
        port: CDP port number (default: 9222)
    """
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)

    # Get absolute path
    abs_file_path = os.path.abspath(file_path)
    print(f"📄 Preparing to upload: {abs_file_path}")

    # Check if Chrome debug is running
    chrome_running = check_chrome_debug_port(port)
    chrome_process = None

    if not chrome_running:
        chrome_process = launch_chrome_debug(port)
        chrome_running = True

    # Connect to Chrome
    playwright, browser = connect_to_chrome(port)

    try:
        # Get the current tab or navigate to URL
        page = None

        if url is None or url == '-':
            # Use current tab
            tab_number = -1
            page = get_chrome_tab_by_number(browser, tab_number)
            current_url = page.url
            print(f"🌐 Current page: {current_url}")
        elif url.startswith('http://') or url.startswith('https://'):
            # Navigate to URL in new tab
            print(f"🌐 Opening new tab: {url}")
            context = browser.contexts[0]
            page = context.new_page()
            page.goto(url, wait_until='domcontentloaded', timeout=15000)
            page.wait_for_timeout(2000)
        else:
            # Try to parse as tab number
            try:
                tab_number = int(url)
                page = get_chrome_tab_by_number(browser, tab_number)
                current_url = page.url
                print(f"🌐 Current page: {current_url}")
            except ValueError:
                raise Exception(f"Invalid argument '{url}': must be a tab number (1, 2, -1, -2, etc.) or URL (http://... or https://...)")

        # Wait for the file input to be present
        print(f"🔍 Looking for file input with selector: {selector}")
        try:
            page.wait_for_selector(selector, timeout=5000)
        except Exception as e:
            print(f"❌ Error: Could not find file input element with selector '{selector}'")
            print(f"   Make sure the page has a file upload button/input")
            sys.exit(1)

        # Upload the file
        print(f"📤 Uploading file...")
        page.set_input_files(selector, abs_file_path)

        # Give it a moment to process
        page.wait_for_timeout(500)

        print(f"✅ File uploaded successfully")

    finally:
        playwright.stop()


def cmd_cpage(args):
    """Handle the cpage command (Chrome CDP version)."""
    url = args.url if args.url != '-' else None
    output = getattr(args, 'output', None)
    output_format = 'yaml' if getattr(args, 'yaml', False) else 'json'
    include_html = getattr(args, 'html', False)
    font_arg = getattr(args, 'font', None)
    extract_page_with_chrome(url, output, output_format=output_format, include_html=include_html, font_filter=font_arg)


def cmd_clist(args):
    """Handle the clist command (Chrome CDP list extraction)."""
    url = args.url if args.url != '-' else None
    min_val = getattr(args, 'min', 5)
    output = getattr(args, 'output', None)
    output_format = 'yaml' if getattr(args, 'yaml', False) else 'json'
    font_arg = getattr(args, 'font', None)

    # Extract list items
    items = extract_list_from_chrome(url, min=min_val, font_filter=font_arg)

    # Output results
    if not YAML_AVAILABLE and output_format == 'yaml':
        print("❌ Error: YAML output requested but PyYAML is not installed.")
        print("   Install with: pip install pyyaml")
        sys.exit(1)

    if output:
        with open(output, 'w') as f:
            if output_format == 'yaml':
                yaml.dump(items, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            else:
                json.dump(items, f, indent=2)
        print(f"💾 Results saved to: {output} ({output_format.upper()} format)")
    else:
        if output_format == 'yaml':
            print("\n" + yaml.dump(items, default_flow_style=False, allow_unicode=True, sort_keys=False))
        else:
            print("\n" + json.dumps(items, indent=2))


def cmd_cupload(args):
    """Handle the cupload command (Chrome CDP file upload)."""
    if not args.file_path:
        print("Error: No file path provided", file=sys.stderr)
        sys.exit(1)

    file_path = args.file_path
    url = args.url if args.url != '-' else None
    selector = getattr(args, 'selector', 'input[type="file"]')

    upload_file_to_chrome(file_path, url, selector)


def click_element_in_chrome(selector: str, url: str = None, port: int = 9222):
    """
    Click an element in Chrome.

    Args:
        selector: CSS selector for the element to click
        url: Optional tab number or URL, or None to use current tab
        port: CDP port number (default: 9222)
    """
    # Check if Chrome debug is running
    chrome_running = check_chrome_debug_port(port)
    chrome_process = None

    if not chrome_running:
        chrome_process = launch_chrome_debug(port)
        chrome_running = True

    # Connect to Chrome
    playwright, browser = connect_to_chrome(port)

    try:
        # Get the current tab or navigate to URL
        page = None

        if url is None or url == '-':
            # Use current tab
            tab_number = -1
            page = get_chrome_tab_by_number(browser, tab_number)
            current_url = page.url
            print(f"🌐 Current page: {current_url}")
        elif url.startswith('http://') or url.startswith('https://'):
            # Navigate to URL in new tab
            print(f"🌐 Opening new tab: {url}")
            context = browser.contexts[0]
            page = context.new_page()
            page.goto(url, wait_until='domcontentloaded', timeout=15000)
            page.wait_for_timeout(2000)
        else:
            # Try to parse as tab number
            try:
                tab_number = int(url)
                page = get_chrome_tab_by_number(browser, tab_number)
                current_url = page.url
                print(f"🌐 Current page: {current_url}")
            except ValueError:
                raise Exception(f"Invalid argument '{url}': must be a tab number (1, 2, -1, -2, etc.) or URL (http://... or https://...)")

        # Wait for the element and click it
        print(f"🔍 Looking for element with selector: {selector}")
        try:
            page.wait_for_selector(selector, timeout=5000)
        except Exception as e:
            print(f"❌ Error: Could not find element with selector '{selector}'")
            sys.exit(1)

        print(f"🖱️  Clicking element...")
        page.click(selector)
        page.wait_for_timeout(500)

        print(f"✅ Element clicked successfully")

    finally:
        playwright.stop()


def type_text_in_chrome(selector: str, text: str, url: str = None, port: int = 9222):
    """
    Type text into an element in Chrome (slower but triggers events).

    Args:
        selector: CSS selector for the element to type into
        text: Text to type
        url: Optional tab number or URL, or None to use current tab
        port: CDP port number (default: 9222)
    """
    # Check if Chrome debug is running
    chrome_running = check_chrome_debug_port(port)
    chrome_process = None

    if not chrome_running:
        chrome_process = launch_chrome_debug(port)
        chrome_running = True

    # Connect to Chrome
    playwright, browser = connect_to_chrome(port)

    try:
        # Get the current tab or navigate to URL
        page = None

        if url is None or url == '-':
            # Use current tab
            tab_number = -1
            page = get_chrome_tab_by_number(browser, tab_number)
            current_url = page.url
            print(f"🌐 Current page: {current_url}")
        elif url.startswith('http://') or url.startswith('https://'):
            # Navigate to URL in new tab
            print(f"🌐 Opening new tab: {url}")
            context = browser.contexts[0]
            page = context.new_page()
            page.goto(url, wait_until='domcontentloaded', timeout=15000)
            page.wait_for_timeout(2000)
        else:
            # Try to parse as tab number
            try:
                tab_number = int(url)
                page = get_chrome_tab_by_number(browser, tab_number)
                current_url = page.url
                print(f"🌐 Current page: {current_url}")
            except ValueError:
                raise Exception(f"Invalid argument '{url}': must be a tab number (1, 2, -1, -2, etc.) or URL (http://... or https://...)")

        # Wait for the element and type into it
        print(f"🔍 Looking for element with selector: {selector}")
        try:
            page.wait_for_selector(selector, timeout=5000)
        except Exception as e:
            print(f"❌ Error: Could not find element with selector '{selector}'")
            sys.exit(1)

        print(f"⌨️  Typing text...")
        page.type(selector, text)
        page.wait_for_timeout(500)

        print(f"✅ Text typed successfully")

    finally:
        playwright.stop()


def fill_input_in_chrome(selector: str, text: str, url: str = None, port: int = 9222):
    """
    Fill an input element in Chrome (faster than type).

    Args:
        selector: CSS selector for the element to fill
        text: Text to fill
        url: Optional tab number or URL, or None to use current tab
        port: CDP port number (default: 9222)
    """
    # Check if Chrome debug is running
    chrome_running = check_chrome_debug_port(port)
    chrome_process = None

    if not chrome_running:
        chrome_process = launch_chrome_debug(port)
        chrome_running = True

    # Connect to Chrome
    playwright, browser = connect_to_chrome(port)

    try:
        # Get the current tab or navigate to URL
        page = None

        if url is None or url == '-':
            # Use current tab
            tab_number = -1
            page = get_chrome_tab_by_number(browser, tab_number)
            current_url = page.url
            print(f"🌐 Current page: {current_url}")
        elif url.startswith('http://') or url.startswith('https://'):
            # Navigate to URL in new tab
            print(f"🌐 Opening new tab: {url}")
            context = browser.contexts[0]
            page = context.new_page()
            page.goto(url, wait_until='domcontentloaded', timeout=15000)
            page.wait_for_timeout(2000)
        else:
            # Try to parse as tab number
            try:
                tab_number = int(url)
                page = get_chrome_tab_by_number(browser, tab_number)
                current_url = page.url
                print(f"🌐 Current page: {current_url}")
            except ValueError:
                raise Exception(f"Invalid argument '{url}': must be a tab number (1, 2, -1, -2, etc.) or URL (http://... or https://...)")

        # Wait for the element and fill it
        print(f"🔍 Looking for element with selector: {selector}")
        try:
            page.wait_for_selector(selector, timeout=5000)
        except Exception as e:
            print(f"❌ Error: Could not find element with selector '{selector}'")
            sys.exit(1)

        print(f"📝 Filling input...")
        page.fill(selector, text)
        page.wait_for_timeout(500)

        print(f"✅ Input filled successfully")

    finally:
        playwright.stop()


def wait_for_element_in_chrome(selector: str, url: str = None, timeout: int = 10000, port: int = 9222):
    """
    Wait for an element to appear in Chrome.

    Args:
        selector: CSS selector for the element to wait for
        url: Optional tab number or URL, or None to use current tab
        timeout: Maximum time to wait in milliseconds (default: 10000)
        port: CDP port number (default: 9222)
    """
    # Check if Chrome debug is running
    chrome_running = check_chrome_debug_port(port)
    chrome_process = None

    if not chrome_running:
        chrome_process = launch_chrome_debug(port)
        chrome_running = True

    # Connect to Chrome
    playwright, browser = connect_to_chrome(port)

    try:
        # Get the current tab or navigate to URL
        page = None

        if url is None or url == '-':
            # Use current tab
            tab_number = -1
            page = get_chrome_tab_by_number(browser, tab_number)
            current_url = page.url
            print(f"🌐 Current page: {current_url}")
        elif url.startswith('http://') or url.startswith('https://'):
            # Navigate to URL in new tab
            print(f"🌐 Opening new tab: {url}")
            context = browser.contexts[0]
            page = context.new_page()
            page.goto(url, wait_until='domcontentloaded', timeout=15000)
            page.wait_for_timeout(2000)
        else:
            # Try to parse as tab number
            try:
                tab_number = int(url)
                page = get_chrome_tab_by_number(browser, tab_number)
                current_url = page.url
                print(f"🌐 Current page: {current_url}")
            except ValueError:
                raise Exception(f"Invalid argument '{url}': must be a tab number (1, 2, -1, -2, etc.) or URL (http://... or https://...)")

        # Wait for the element
        print(f"⏳ Waiting for element with selector: {selector}")
        try:
            page.wait_for_selector(selector, timeout=timeout)
            print(f"✅ Element found!")
        except Exception as e:
            print(f"❌ Error: Timeout waiting for element with selector '{selector}'")
            sys.exit(1)

    finally:
        playwright.stop()


def execute_javascript_in_chrome(javascript: str, url: str = None, port: int = 9222):
    """
    Execute JavaScript in Chrome and return the result.

    Args:
        javascript: JavaScript code to execute
        url: Optional tab number or URL, or None to use current tab
        port: CDP port number (default: 9222)
    """
    # Check if Chrome debug is running
    chrome_running = check_chrome_debug_port(port)
    chrome_process = None

    if not chrome_running:
        chrome_process = launch_chrome_debug(port)
        chrome_running = True

    # Connect to Chrome
    playwright, browser = connect_to_chrome(port)

    try:
        # Get the current tab or navigate to URL
        page = None

        if url is None or url == '-':
            # Use current tab
            tab_number = -1
            page = get_chrome_tab_by_number(browser, tab_number)
            current_url = page.url
            print(f"🌐 Current page: {current_url}")
        elif url.startswith('http://') or url.startswith('https://'):
            # Navigate to URL in new tab
            print(f"🌐 Opening new tab: {url}")
            context = browser.contexts[0]
            page = context.new_page()
            page.goto(url, wait_until='domcontentloaded', timeout=15000)
            page.wait_for_timeout(2000)
        else:
            # Try to parse as tab number
            try:
                tab_number = int(url)
                page = get_chrome_tab_by_number(browser, tab_number)
                current_url = page.url
                print(f"🌐 Current page: {current_url}")
            except ValueError:
                raise Exception(f"Invalid argument '{url}': must be a tab number (1, 2, -1, -2, etc.) or URL (http://... or https://...)")

        # Execute JavaScript
        print(f"⚡ Executing JavaScript...")
        result = page.evaluate(javascript)

        print(f"✅ JavaScript executed successfully")

        # Print result if there is one
        if result is not None:
            print(f"\nResult:")
            if isinstance(result, (dict, list)):
                print(json.dumps(result, indent=2))
            else:
                print(result)

        return result

    finally:
        playwright.stop()


def cmd_cclick(args):
    """Handle the cclick command (Chrome CDP click)."""
    if not args.selector:
        print("Error: No selector provided", file=sys.stderr)
        sys.exit(1)

    selector = args.selector
    url = args.url if args.url != '-' else None

    click_element_in_chrome(selector, url)


def cmd_ctype(args):
    """Handle the ctype command (Chrome CDP type)."""
    if not args.selector:
        print("Error: No selector provided", file=sys.stderr)
        sys.exit(1)

    if not args.text:
        print("Error: No text provided", file=sys.stderr)
        sys.exit(1)

    selector = args.selector
    text = args.text
    url = args.url if args.url != '-' else None

    type_text_in_chrome(selector, text, url)


def cmd_cfill(args):
    """Handle the cfill command (Chrome CDP fill)."""
    if not args.selector:
        print("Error: No selector provided", file=sys.stderr)
        sys.exit(1)

    if not args.text:
        print("Error: No text provided", file=sys.stderr)
        sys.exit(1)

    selector = args.selector
    text = args.text
    url = args.url if args.url != '-' else None

    fill_input_in_chrome(selector, text, url)


def cmd_cwait(args):
    """Handle the cwait command (Chrome CDP wait)."""
    if not args.selector:
        print("Error: No selector provided", file=sys.stderr)
        sys.exit(1)

    selector = args.selector
    url = args.url if args.url != '-' else None
    timeout = getattr(args, 'timeout', 10000)

    wait_for_element_in_chrome(selector, url, timeout)


def cmd_cexec(args):
    """Handle the cexec command (Chrome CDP execute JavaScript)."""
    if not args.javascript:
        print("Error: No JavaScript provided", file=sys.stderr)
        sys.exit(1)

    javascript = args.javascript
    url = args.url if args.url != '-' else None

    execute_javascript_in_chrome(javascript, url)


def handle_native_file_dialog(file_path: str, wait_time: float = 1.0):
    """
    Handle macOS native file picker dialog using AppleScript.

    Args:
        file_path: Absolute path to file to select
        wait_time: Time to wait for dialog to appear in seconds (default: 1.0)
    """
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)

    # Get absolute path and split into directory and filename
    abs_file_path = os.path.abspath(file_path)
    directory = os.path.dirname(abs_file_path)
    filename = os.path.basename(abs_file_path)

    print(f"📄 Preparing to select file in native dialog: {abs_file_path}")
    print(f"   Directory: {directory}")
    print(f"   Filename: {filename}")

    # Wait for dialog to appear
    print(f"⏳ Waiting {wait_time}s for native file dialog to appear...")
    time.sleep(wait_time)

    # Use AppleScript to control the native file dialog
    # Use Cmd+Shift+G to navigate to directory, then type filename
    applescript = '''
    tell application "Google Chrome" to activate
    delay 0.3

    tell application "System Events"
        tell process "Google Chrome"
            -- Press Cmd+Shift+G to open "Go to folder"
            keystroke "g" using {command down, shift down}
            delay 0.5

            -- Paste the directory path (from clipboard)
            keystroke "v" using {command down}
            delay 0.5

            -- Press Enter to navigate to the directory
            keystroke return
            delay 0.8

            -- Type the filename directly to filter and select
            keystroke "FILENAME_PLACEHOLDER"
            delay 0.8

            -- Press Enter to open the file
            keystroke return
            delay 0.3

            -- Press Enter again in case first one just selected
            keystroke return
        end tell
    end tell
    '''

    # Replace placeholder with actual filename (needs proper escaping)
    # Use simple character-by-character replacement
    applescript = applescript.replace('FILENAME_PLACEHOLDER', filename)

    print(f"🎯 Sending file path to native dialog...")

    # Copy directory path to clipboard (not the full file path!)
    subprocess.run(['pbcopy'], input=directory.encode(), check=True)

    # Run the AppleScript
    result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Error controlling native dialog: {result.stderr}")
        sys.exit(1)

    print(f"✅ File selected in native dialog successfully")


def cmd_cnativefile(args):
    """Handle the cnativefile command (control native macOS file dialog)."""
    if not args.file_path:
        print("Error: No file path provided", file=sys.stderr)
        sys.exit(1)

    file_path = args.file_path
    wait_time = getattr(args, 'wait_time', 1.0)

    handle_native_file_dialog(file_path, wait_time)


def cmd_x(args):
    """Handle the x (extended/macro) command."""
    if not args.macro:
        print("Error: No macro specified", file=sys.stderr)
        print("Available macros: excal", file=sys.stderr)
        sys.exit(1)

    macro = args.macro

    if macro == 'excal':
        # Upload file to Excalidraw
        if not args.args or len(args.args) < 1:
            print("Error: excal requires a file path", file=sys.stderr)
            print("Usage: ctrl x excal <file>", file=sys.stderr)
            sys.exit(1)

        file_path = args.args[0]

        # Check if file exists
        if not os.path.exists(file_path):
            print(f"❌ Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)

        print(f"🚀 Uploading {file_path} to Excalidraw...")

        # Step 1: Reset the canvas to avoid "replace contents" dialog
        print(f"📌 Step 1/4: Resetting canvas...")
        click_element_in_chrome(".main-menu-trigger", url='-1')
        time.sleep(0.3)
        click_element_in_chrome(".dropdown-menu-item:has-text('Reset the canvas')", url='-1')
        time.sleep(0.3)
        click_element_in_chrome("button:has-text('Confirm')", url='-1')
        time.sleep(0.5)

        # Step 2: Click the hamburger menu
        print(f"📌 Step 2/4: Opening main menu...")
        click_element_in_chrome(".main-menu-trigger", url='-1')

        # Small delay for menu to appear
        time.sleep(0.3)

        # Step 3: Click the Open button
        print(f"📌 Step 3/4: Clicking 'Open' button...")
        click_element_in_chrome(".dropdown-menu-item:has-text('Open')", url='-1')

        # Step 4: Handle native file dialog
        print(f"📌 Step 4/4: Selecting file in native dialog...")
        handle_native_file_dialog(file_path, wait_time=1.5)

        # Small delay for file to load
        time.sleep(1.0)

        print(f"✅ Upload complete!")

    elif macro == 'excalsave':
        # Save current Excalidraw to file
        if not args.args or len(args.args) < 1:
            print("Error: excalsave requires a file path", file=sys.stderr)
            print("Usage: ctrl x excalsave <file>", file=sys.stderr)
            sys.exit(1)

        file_path = args.args[0]

        # Get absolute path
        abs_file_path = os.path.abspath(file_path)

        print(f"💾 Saving Excalidraw to {abs_file_path}...")

        # Extract scene data from localStorage using JavaScript
        javascript = '''
        (() => {
            const elements = JSON.parse(localStorage.getItem('excalidraw') || '[]');
            const state = JSON.parse(localStorage.getItem('excalidraw-state') || '{}');

            // Build .excalidraw file format
            const sceneData = {
                type: "excalidraw",
                version: 2,
                source: "https://excalidraw.com",
                elements: elements,
                appState: {
                    gridSize: state.gridSize || 20,
                    viewBackgroundColor: state.viewBackgroundColor || "#ffffff"
                },
                files: {}
            };

            return JSON.stringify(sceneData, null, 0);
        })()
        '''

        try:
            # Execute JavaScript to get scene data
            scene_json = execute_javascript_in_chrome(javascript, url='-1')

            # Write to file
            with open(abs_file_path, 'w') as f:
                f.write(scene_json)

            print(f"✅ Saved to {abs_file_path}")

        except Exception as e:
            print(f"❌ Error saving file: {e}", file=sys.stderr)
            sys.exit(1)

    else:
        print(f"Error: Unknown macro '{macro}'", file=sys.stderr)
        print("Available macros: excal, excalsave", file=sys.stderr)
        sys.exit(1)


def print_usage():
    """Print custom usage information."""
    usage_text = """CTRL - Environment Control Tool

Usage: ctrl <command> [options]

Commands:
    search <query>              Perform Google search
        --new-tab               Open search in new Safari tab
        --results <N>           Parse and return N search results
        --json                  Output results as JSON

    surf <url>                  Navigate Safari to URL (opens in new tab by default)
        --same-tab              Open URL in current Safari tab instead

    navigate <url>              Navigate Safari to URL (opens in current tab by default)
        --new-tab               Open URL in new Safari tab

    new-tab                     Create new empty Safari tab

    box <command>               Execute command in box tmux session
    box2-9 <command>            Execute command in boxN tmux session
    outbox [lines]              Get last N lines from box session (default: 50)
    outbox2-9 [lines]           Get last N lines from boxN session

    jsearch <query>             Perform Google search and return JSON results
        --output <file>         Save results to file (default: print to stdout)

    jpage <url>                 Navigate to URL and extract page content as JSON
        --output <file>         Save results to file (default: print to stdout)

    jgetlist                    Extract repeating list structure from current page
        --output <file>         Save results to file (default: print to stdout)
        --min-items <N>         Minimum items to consider a list (default: 3)

    tab <url>                   Open URL in new tab (keeps current tab active)

Playwright-based Commands (Advanced):
    jjpage <url|->              Extract page content using Playwright
        <url>                   URL to extract from
        -                       Use current Safari page URL
        --output <file>         Save results to file (default: print to stdout)

Chrome CDP Commands (Uses your real Chrome browser):
    cpage <tab|url>             Extract page content via Chrome CDP
        <tab>                   Tab number: 1, 2, 3... (first, second, third tab)
                                           -, -1 (last tab)
                                           -2, -3... (second-to-last, third-to-last)
        <url>                   URL to open in new Chrome tab (http://... or https://...)
        --output <file>         Save results to file (default: print to stdout)
        --yaml                  Output in YAML format instead of JSON
        --html                  Include full HTML in output (default: false)
        --font [N]              Font format/filter (default: f1/f2/f3 prefix):
                                  --font or --font -  : legacy " ~:~ " suffix format
                                  --font 5           : filter to show only f1-f5 fonts

    cclick <selector> [tab]     Click element in Chrome via CDP
        <selector>              CSS selector for element to click
        <tab>                   Tab number or URL (default: last tab)

    ctype <selector> <text> [tab]  Type text into element (triggers keyboard events)
        <selector>              CSS selector for element
        <text>                  Text to type
        <tab>                   Tab number or URL (default: last tab)

    cfill <selector> <text> [tab]  Fill input element (faster than type)
        <selector>              CSS selector for element
        <text>                  Text to fill
        <tab>                   Tab number or URL (default: last tab)

    cwait <selector> [tab]      Wait for element to appear
        <selector>              CSS selector to wait for
        <tab>                   Tab number or URL (default: last tab)
        --timeout <ms>          Timeout in milliseconds (default: 10000)

    cexec <javascript> [tab]    Execute JavaScript in Chrome
        <javascript>            JavaScript code to execute
        <tab>                   Tab number or URL (default: last tab)

    cnativefile <file>          Handle macOS native file picker dialog
        <file>                  Path to file to select
        --wait-time <sec>       Seconds to wait for dialog (default: 1.0)

Extended Commands (Macros):
    x excal <file>              Load .excalidraw file into Excalidraw
        <file>                  Path to .excalidraw file to load

    x excalsave <file>          Save current Excalidraw drawing to file
        <file>                  Path where to save .excalidraw file

Global Options:
    -h, --help                  Show this help message
    -v, --version               Show version information
    --verbose                   Enable verbose logging

Examples:
    ctrl search "Python documentation"
    ctrl search --new-tab --results 5 "AI research"
    ctrl search --json "machine learning"
    ctrl surf "https://github.com"              # Opens in new tab
    ctrl surf --same-tab "https://example.com"   # Opens in current tab
    ctrl new-tab
    ctrl box "ls -la"
    ctrl box "python script.py"
    ctrl outbox
    ctrl outbox 100
    ctrl jsearch "machine learning jobs"
    ctrl jsearch "AI startups" --output results.json
    ctrl jpage "https://example.com"
    ctrl jpage "thelevel.ai" --output page_content.json
    ctrl jgetlist
    ctrl jgetlist --output jobs.json
    ctrl jgetlist --min-items 5
    ctrl tab "github.com"
    ctrl tab "thelevel.ai"
    ctrl cclick "button.submit"
    ctrl ctype "input[name='search']" "hello world"
    ctrl cexec "alert('Hello!')"
    ctrl x excal ~/my-drawing.excalidraw
    ctrl x excalsave ~/my-drawing.excalidraw
"""
    print(usage_text)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="CTRL - Environment Control Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False  # We'll handle help ourselves
    )

    # Global options
    parser.add_argument('-h', '--help', action='store_true',
                        help='Show help message')
    parser.add_argument('-v', '--version', action='store_true',
                        help='Show version information')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Search command
    search_parser = subparsers.add_parser('search', help='Perform Google search')
    search_parser.add_argument('query', nargs='*', help='Search query')
    search_parser.add_argument('--new-tab', action='store_true',
                              help='Open search in new Safari tab')
    search_parser.add_argument('--results', type=int, nargs='?', const=10,
                              help='Parse N search results (default: 10 if flag present)')
    search_parser.add_argument('--json', action='store_true',
                              help='Output results as JSON')

    # Navigate command
    nav_parser = subparsers.add_parser('navigate', help='Navigate to URL')
    nav_parser.add_argument('url', nargs=1, help='URL to navigate to')
    nav_parser.add_argument('--new-tab', action='store_true',
                           help='Open URL in new Safari tab')

    # Surf command (alias for navigate, but defaults to new tab)
    surf_parser = subparsers.add_parser('surf', help='Navigate to URL in new tab')
    surf_parser.add_argument('url', nargs=1, help='URL to navigate to')
    surf_parser.add_argument('--same-tab', dest='new_tab', action='store_false',
                           help='Open URL in current Safari tab instead of new tab')
    surf_parser.set_defaults(new_tab=True)

    # New tab command
    subparsers.add_parser('new-tab', help='Create new empty Safari tab')

    # Trot command - execute in persistent tmux session (primary name)
    trot_parser = subparsers.add_parser('trot', help='Execute command in trot tmux session')
    trot_parser.add_argument('box_command', nargs='+', help='Command to execute')

    # Box command - alias for trot (backward compatibility)
    box_parser = subparsers.add_parser('box', help='Execute command in box tmux session (alias for trot)')
    box_parser.add_argument('box_command', nargs='+', help='Command to execute in box')

    # Outbox command - get output from session
    outbox_parser = subparsers.add_parser('outbox', help='Get output from trot/box tmux session')
    outbox_parser.add_argument('lines', nargs='?', type=int, default=50, help='Number of lines to retrieve (default: 50)')

    # Numbered box/outbox commands (box2-box9, outbox2-outbox9)
    for n in range(2, 10):
        bp = subparsers.add_parser(f'box{n}', help=f'Execute command in box{n} tmux session')
        bp.add_argument('box_command', nargs='+', help='Command to execute')
        bp.set_defaults(session_name=f'box{n}')

        op = subparsers.add_parser(f'outbox{n}', help=f'Get output from box{n} tmux session')
        op.add_argument('lines', nargs='?', type=int, default=50, help='Number of lines to retrieve')
        op.set_defaults(session_name=f'box{n}')

    # JSON Search command
    jsearch_parser = subparsers.add_parser('jsearch', help='Perform Google search and return JSON results')
    jsearch_parser.add_argument('query', help='Search query string')
    jsearch_parser.add_argument('--output', '-o', help='Output file path (default: print to stdout)')

    # JSON Page command
    jpage_parser = subparsers.add_parser('jpage', help='Navigate to URL and extract page content as JSON')
    jpage_parser.add_argument('url', help='URL to navigate to and extract content from')
    jpage_parser.add_argument('--output', '-o', help='Output file path (default: print to stdout)')

    # Tab command
    tab_parser = subparsers.add_parser('tab', help='Open URL in new tab without extracting content')
    tab_parser.add_argument('url', help='URL to open in new tab')

    # JSON Get List command
    jgetlist_parser = subparsers.add_parser('jgetlist', help='Extract repeating list structure from current page')
    jgetlist_parser.add_argument('--output', '-o', help='Output file path (default: print to stdout)')
    jgetlist_parser.add_argument('--min-items', type=int, default=3, help='Minimum number of items to consider a list (default: 3)')

    # Playwright-based jjpage command
    jjpage_parser = subparsers.add_parser('jjpage', help='Extract page content using Playwright (advanced)')
    jjpage_parser.add_argument('url', nargs='?', default='-', help='URL to extract from, or "-" for current Safari page')
    jjpage_parser.add_argument('--output', '-o', help='Output file path (default: print to stdout)')

    # Chrome CDP cpage command
    cpage_parser = subparsers.add_parser('cpage', help='Extract page content using Chrome CDP')
    cpage_parser.add_argument('url', nargs='?', default='-', help='Tab number (1, 2, -1, -2...), URL (http://...), or "-" for last tab')
    cpage_parser.add_argument('--output', '-o', help='Output file path (default: print to stdout)')
    cpage_parser.add_argument('--yaml', action='store_true', help='Output in YAML format instead of JSON')
    cpage_parser.add_argument('--html', action='store_true', help='Include full HTML in output')
    cpage_parser.add_argument('--font', nargs='?', const='-', metavar='N', help='Font format: no value or "-" for legacy " ~:~ " suffix, integer N to filter and show only fonts f1-fN')

    # Chrome CDP clist command
    clist_parser = subparsers.add_parser('clist', help='Extract list structure from Chrome page by finding common font')
    clist_parser.add_argument('url', nargs='?', default='-', help='Tab number (1, 2, -1, -2...), URL (http://...), or "-" for last tab')
    clist_parser.add_argument('--output', '-o', help='Output file path (default: print to stdout)')
    clist_parser.add_argument('--yaml', action='store_true', help='Output in YAML format instead of JSON')
    clist_parser.add_argument('--min', type=int, default=5, help='Minimum font count to consider as list item name (default: 5)')
    clist_parser.add_argument('--font', nargs='?', const='-', metavar='N', help='Font format: no value or "-" for legacy " ~:~ " suffix, integer N to filter and show only fonts f1-fN')

    # Chrome CDP cupload command
    cupload_parser = subparsers.add_parser('cupload', help='Upload file to Chrome page via CDP')
    cupload_parser.add_argument('file_path', help='Path to file to upload')
    cupload_parser.add_argument('url', nargs='?', default='-', help='Tab number (1, 2, -1, -2...), URL (http://...), or "-" for last tab (default: -)')
    cupload_parser.add_argument('--selector', default='input[type="file"]', help='CSS selector for file input element (default: input[type="file"])')

    # Chrome CDP cclick command
    cclick_parser = subparsers.add_parser('cclick', help='Click element in Chrome via CDP')
    cclick_parser.add_argument('selector', help='CSS selector for element to click')
    cclick_parser.add_argument('url', nargs='?', default='-', help='Tab number (1, 2, -1, -2...), URL (http://...), or "-" for last tab (default: -)')

    # Chrome CDP ctype command
    ctype_parser = subparsers.add_parser('ctype', help='Type text into element in Chrome via CDP')
    ctype_parser.add_argument('selector', help='CSS selector for element to type into')
    ctype_parser.add_argument('text', help='Text to type')
    ctype_parser.add_argument('url', nargs='?', default='-', help='Tab number (1, 2, -1, -2...), URL (http://...), or "-" for last tab (default: -)')

    # Chrome CDP cfill command
    cfill_parser = subparsers.add_parser('cfill', help='Fill input element in Chrome via CDP (faster than type)')
    cfill_parser.add_argument('selector', help='CSS selector for element to fill')
    cfill_parser.add_argument('text', help='Text to fill')
    cfill_parser.add_argument('url', nargs='?', default='-', help='Tab number (1, 2, -1, -2...), URL (http://...), or "-" for last tab (default: -)')

    # Chrome CDP cwait command
    cwait_parser = subparsers.add_parser('cwait', help='Wait for element to appear in Chrome via CDP')
    cwait_parser.add_argument('selector', help='CSS selector for element to wait for')
    cwait_parser.add_argument('url', nargs='?', default='-', help='Tab number (1, 2, -1, -2...), URL (http://...), or "-" for last tab (default: -)')
    cwait_parser.add_argument('--timeout', type=int, default=10000, help='Timeout in milliseconds (default: 10000)')

    # Chrome CDP cexec command
    cexec_parser = subparsers.add_parser('cexec', help='Execute JavaScript in Chrome via CDP')
    cexec_parser.add_argument('javascript', help='JavaScript code to execute')
    cexec_parser.add_argument('url', nargs='?', default='-', help='Tab number (1, 2, -1, -2...), URL (http://...), or "-" for last tab (default: -)')

    # Native file dialog command
    cnativefile_parser = subparsers.add_parser('cnativefile', help='Handle macOS native file picker dialog')
    cnativefile_parser.add_argument('file_path', help='Path to file to select in native dialog')
    cnativefile_parser.add_argument('--wait-time', type=float, default=1.0, help='Time to wait for dialog to appear in seconds (default: 1.0)')

    # Extended/macro commands
    x_parser = subparsers.add_parser('x', help='Extended/macro commands')
    x_parser.add_argument('macro', help='Macro name (excal, ...)')
    x_parser.add_argument('args', nargs='*', help='Arguments for the macro')

    # Edit command
    edit_parser = subparsers.add_parser('edit', help='Edit file in Sublime Text')
    edit_parser.add_argument('file_path', help='Path to file to edit')

    return parser.parse_args()


def cmd_edit(args):
    """Handle the edit command - opens file in Sublime Text."""
    file_path = args.file_path

    try:
        subprocess.run(['open', '-a', 'Sublime Text', file_path], check=True)
    except Exception as e:
        print(f"Error opening file in Sublime: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    args = parse_arguments()

    # Handle version first
    if args.version:
        print(f"CTRL version {__version__}")
        sys.exit(0)

    # Handle help
    if args.help or not args.command:
        print_usage()
        sys.exit(0)

    # Setup logging
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    # Dispatch to command handlers
    command_handlers = {
        'search': cmd_search,
        'navigate': cmd_navigate,
        'surf': cmd_navigate,  # alias for navigate
        'new-tab': cmd_new_tab,
        'trot': cmd_box,
        'box': cmd_box,  # alias for trot
        'outbox': cmd_outbox,
        **{f'box{n}': cmd_box for n in range(2, 10)},
        **{f'outbox{n}': cmd_outbox for n in range(2, 10)},
        'jsearch': cmd_jsearch,
        'jpage': cmd_jpage,
        'jgetlist': cmd_jgetlist,
        'jjpage': cmd_jjpage,
        'cpage': cmd_cpage,
        'clist': cmd_clist,
        'cupload': cmd_cupload,
        'cclick': cmd_cclick,
        'ctype': cmd_ctype,
        'cfill': cmd_cfill,
        'cwait': cmd_cwait,
        'cexec': cmd_cexec,
        'cnativefile': cmd_cnativefile,
        'x': cmd_x,
        'tab': cmd_tab,
        'edit': cmd_edit,
    }

    handler = command_handlers.get(args.command)
    if handler:
        handler(args)
    else:
        print(f"Error: Unknown command '{args.command}'", file=sys.stderr)
        print("Use --help for usage information", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()# This won't work — ctrl is its own script. Let me check the actual implementation.
