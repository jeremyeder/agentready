#!/bin/bash
# Update release documentation with current version
# Called by semantic-release during release process

set -e

VERSION=${1:-$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')}
TODAY=$(date +%Y-%m-%d)

echo "Updating release documentation to version $VERSION (date: $TODAY)"

# Update RELEASE_PROCESS.md Last Updated date
sed -i.bak "s/\*\*Last Updated\*\*: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/**Last Updated**: $TODAY/" docs/RELEASE_PROCESS.md

# Update release-process-visualization.html timestamp in footer
if [ -f "docs/release-process-visualization.html" ]; then
    # Update any hardcoded version references in visualization
    sed -i.bak "s/v[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*/v$VERSION/g" docs/release-process-visualization.html

    # The JavaScript already sets the timestamp dynamically, but we can add a data attribute
    sed -i.bak "s/data-version=\"[^\"]*\"/data-version=\"$VERSION\"/" docs/release-process-visualization.html || \
        sed -i.bak "s/<body>/<body data-version=\"$VERSION\">/" docs/release-process-visualization.html
fi

# Clean up backup files
rm -f docs/RELEASE_PROCESS.md.bak docs/release-process-visualization.html.bak

echo "✓ Release documentation updated successfully"
echo "  - Version: $VERSION"
echo "  - Date: $TODAY"
