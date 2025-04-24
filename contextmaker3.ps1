<#
.SYNOPSIS
Generates a compact text representation of the current directory tree,
prepends system information, formats it as Markdown, and saves it
to 'directory-tree.md'.

.DESCRIPTION
Scans the current directory recursively ($PWD) and outputs a minimal text
format showing the hierarchy of folders and files. Includes OS and PowerShell
version. Wraps the tree structure in Markdown code fences. Designed to provide
directory context to LLMs while minimizing token usage. Uses a single
space for indentation and a trailing slash (/) to denote directories.
Common noisy folders like .git, node_modules, etc., are excluded.
The output is saved to 'directory-tree.md' in the current directory.
#>

# --- Configuration ---
$IndentString = ' ' # Minimal indent
$OutputFileName = 'directory-tree.md'
$IgnoreFolders = @( # Case-sensitive list of folder names to ignore
    '.git', 'node_modules', '__pycache__', '.vscode', '.idea', 'bin', 'obj',
    'dist', 'build', '.svn', 'CVS', 'target', '.terraform', '.serverless',
    'venv', '.venv', 'env', '.env', 'temp', 'tmp'
)
# --- End Configuration ---

# --- Helper Function for Recursion (Unchanged) ---
function Get-TreeRecursive {
    param(
        [string]$CurrentPath,
        [int]$CurrentDepth
    )

    # Get items, handle potential access errors gracefully, sort folders first
    try {
        # Note: Default Get-ChildItem often hides system/hidden files.
        # We don't use -Force here to keep the output minimal by default.
        # Add -Force if you *need* to see hidden items not in IgnoreFolders.
        $items = Get-ChildItem -Path $CurrentPath -ErrorAction SilentlyContinue | Sort-Object @{Expression='PSIsContainer'; Descending=$true}, Name
    } catch {
        Write-Warning "Could not access '$CurrentPath': $($_.Exception.Message)"
        return # Stop processing this path if inaccessible
    }

    # --- Process Items at Current Level ---
    foreach ($item in $items) {
        $indent = $IndentString * $CurrentDepth

        if ($item.PSIsContainer) {
            # Check if this directory name is in the ignore list
            if ($IgnoreFolders -contains $item.Name) {
                # Write-Verbose "Ignoring directory: $($item.FullName)" # Uncomment for debugging
                continue # Skip this directory and its contents
            }

            # Output directory name
            "$($indent)$($item.Name)/"

            # Recurse deeper
            Get-TreeRecursive -CurrentPath $item.FullName -CurrentDepth ($CurrentDepth + 1)

        } else {
            # Output file name
            "$($indent)$($item.Name)"
        }
    }
}

# --- Main Script Logic ---

# Get the starting path (current directory)
$startPath = $PWD.Path
$outputFilePath = Join-Path -Path $startPath -ChildPath $OutputFileName

Write-Host "Gathering system information..."
Write-Host "Generating directory tree for '$startPath'..."
Write-Host "Ignoring folders: $($IgnoreFolders -join ', ')"

# Initialize an array to hold all output lines
$outputLines = @()

# --- System Information ---
$outputLines += '# System Information'
$outputLines += ''
# These MUST use double quotes for subexpression evaluation: $($...)
$outputLines += "- OS: $((Get-CimInstance Win32_OperatingSystem).Caption)"
$outputLines += "- PowerShell Version: $($PSVersionTable.PSVersion.ToString())"
$outputLines += ''

# --- Recursive Directory Structure ---
# This MUST use double quotes for subexpression evaluation: $($PWD.Path) or $startPath
$outputLines += "# Recursive Directory Structure: $startPath"
$outputLines += ''
$outputLines += '```' # Start Markdown code block

# Capture the tree structure output from the recursive function
# Use -ErrorAction SilentlyContinue on the function call as well in case of top-level errors
$treeLines = Get-TreeRecursive -CurrentPath $startPath -CurrentDepth 0 -ErrorAction SilentlyContinue

# Add the generated tree lines to the output
if ($null -ne $treeLines) {
    $outputLines += $treeLines
} else {
    $outputLines += "(No files or folders found, or error accessing root)"
}


$outputLines += '```' # End Markdown code block

# Save the combined output to the markdown file
try {
    $outputLines | Out-File -FilePath $outputFilePath -Encoding UTF8 -Force
    Write-Host "Success! Directory tree with system info saved to: $outputFilePath"
} catch {
    Write-Error "Failed to write to '$outputFilePath': $($_.Exception.Message)"
}