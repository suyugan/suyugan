#!/bin/bash
# ClawHub Skill Search CLI
# Base URL: https://skills.droyd.ai

BASE_URL="https://skills.droyd.ai"

usage() {
    echo "Usage: skillhub.sh <command> [options]"
    echo ""
    echo "Commands:"
    echo "  search <query>     Search for skills"
    echo "  trending           Browse trending skills"
    echo "  detail <slug>      Get skill details"
    echo "  content <slug>     Fetch skill content"
    echo ""
    echo "Options:"
    echo "  --categories <cat> Filter by categories (comma-separated)"
    echo "  --limit <n>        Max results"
    echo "  --window <period>  Time window (7d, 30d)"
    echo "  --extract          Extract to /tmp/openclaw-skills/"
}

search() {
    local query="$1"
    shift
    local categories=""
    local limit=10
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --categories) categories="$2"; shift 2 ;;
            --limit) limit="$2"; shift 2 ;;
            *) shift ;;
        esac
    done
    
    local url="${BASE_URL}/api/skills/search?q=$(echo "$query" | sed 's/ /%20/g')&limit=$limit"
    [[ -n "$categories" ]] && url="${url}&categories=$categories"
    
    curl -s "$url" | jq -r '.skills[] | "[\(.slug)] \(.name) - \(.description[:80])..."' 2>/dev/null || curl -s "$url"
}

trending() {
    local categories=""
    local window="7d"
    local limit=20
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --categories) categories="$2"; shift 2 ;;
            --window) window="$2"; shift 2 ;;
            --limit) limit="$2"; shift 2 ;;
            *) shift ;;
        esac
    done
    
    local url="${BASE_URL}/api/skills/trending?window=$window&limit=$limit"
    [[ -n "$categories" ]] && url="${url}&categories=$categories"
    
    curl -s "$url" | jq -r '.skills[] | "[\(.slug)] ⭐\(.stars // 0) \(.name) - \(.description[:60])..."' 2>/dev/null || curl -s "$url"
}

detail() {
    local slug="$1"
    curl -s "${BASE_URL}/api/skills/${slug}" | jq . 2>/dev/null || curl -s "${BASE_URL}/api/skills/${slug}"
}

content() {
    local slug="$1"
    local extract=false
    
    shift
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --extract) extract=true; shift ;;
            *) shift ;;
        esac
    done
    
    local response=$(curl -s "${BASE_URL}/api/skills/${slug}/content")
    
    if $extract; then
        local skill_name=$(echo "$slug" | sed 's|.*/||')
        local dir="/tmp/openclaw-skills/${skill_name}"
        mkdir -p "$dir"
        
        # Extract SKILL.md
        echo "$response" | jq -r '.content // .skill_md // .' > "${dir}/SKILL.md" 2>/dev/null || echo "$response" > "${dir}/SKILL.md"
        
        echo "Extracted to: $dir"
        ls -la "$dir"
    else
        echo "$response" | jq -r '.content // .skill_md // .' 2>/dev/null || echo "$response"
    fi
}

case "$1" in
    search) shift; search "$@" ;;
    trending) shift; trending "$@" ;;
    detail) shift; detail "$@" ;;
    content) shift; content "$@" ;;
    *) usage ;;
esac
