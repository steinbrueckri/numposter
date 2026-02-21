default:
    @just --list

font_url := "https://github.com/mozilla/Fira/raw/master/otf/FiraMono-Regular.otf"

# Download Fira Mono font into fonts/
fetch-font:
    mkdir -p fonts
    curl -Lo fonts/FiraMono-Regular.otf {{ font_url }}

# Generate .tex files and compile to PDF
# poster: 9|11|primes|collatz|pi|all
# scheme: print|matrix|blueprint|ember|all
# paper: a3plus|a3|a4|all
build poster="all" scheme="all" paper="all":
    uv run python -m src.generate_poster {{ poster }} {{ scheme }} {{ paper }}
    while IFS= read -r f; do [ -n "$f" ] && xelatex -interaction=nonstopmode -output-directory=build "$f"; done < build/.generated

# Build digit sum 9 poster
build-9:
    just build 9 all

# Build alternating sum 11 poster
build-11:
    just build 11 all

# Build primes poster
build-primes:
    just build primes all

# Build Collatz poster
build-collatz:
    just build collatz all

# Build π poster
build-pi:
    just build pi all

# Build all posters
build-all:
    just build all all

latex_image := "blang/latex:ctanfull"

# Generate .tex files and compile to PDF inside a Docker container
# poster: 9|11|primes|collatz|pi|all
# scheme: print|matrix|blueprint|ember|all
# paper: a3plus|a3|a4|all
build-docker poster="all" scheme="all" paper="all":
    uv run python -m src.generate_poster {{ poster }} {{ scheme }} {{ paper }}
    while IFS= read -r f; do [ -n "$f" ] && docker run --rm -v "$PWD:/src" -w /src {{ latex_image }} xelatex -interaction=nonstopmode -output-directory=build "$f"; done < build/.generated

# Run all tests but fail fast
ci:
    uv run rumdl check README.md
    uv run ruff check src/

# Clean build artifacts
clean:
    rm -rf build/*.tex
    rm -rf build/*.log
    rm -rf build/*.aux
