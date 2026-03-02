#!/bin/bash
# GitHub仓库创建和推送脚本

echo "================================"
echo "🚀 GitHub仓库创建工具"
echo "================================"
echo ""

# 仓库信息
USERNAME="hayhaps"
REPO_NAME="network-diagnostic-tool"
REPO_DESC="网络故障排查工具 - 功能全面的网络诊断工具"

echo "📋 仓库信息："
echo "   用户名: $USERNAME"
echo "   仓库名: $REPO_NAME"
echo "   描述: $REPO_DESC"
echo ""

# 检查是否需要认证
if ! gh auth status &>/dev/null | grep -q "Logged in"; then
    echo "⚠️  GitHub CLI未认证"
    echo ""
    echo "请选择认证方式："
    echo ""
    echo "方式1: 网页认证（推荐）"
    echo "  运行: gh auth login --web"
    echo "  然后在浏览器中完成认证"
    echo ""
    echo "方式2: Token认证"
    echo "  1. 访问: https://github.com/settings/tokens"
    echo "  2. 生成Token（勾选repo权限）"
    echo "  3. 运行: export GITHUB_TOKEN=你的Token"
    echo ""
    read -p "认证完成后按回车继续..."
fi

# 检查仓库是否存在
echo ""
echo "🔍 检查仓库..."
REPO_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://github.com/${USERNAME}/${REPO_NAME})

if [ "$REPO_STATUS" = "200" ]; then
    echo "✅ 仓库已存在"
    echo ""
    echo "📤 正在推送代码..."
    cd "/Users/hayha/Desktop/ios project"
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "================================"
        echo "✅ 推送成功！"
        echo "================================"
        echo ""
        echo "🌐 仓库地址: https://github.com/${USERNAME}/${REPO_NAME}"
        echo ""
    else
        echo ""
        echo "❌ 推送失败，请检查权限"
        echo ""
    fi
else
    echo "❌ 仓库不存在 (HTTP $REPO_STATUS)"
    echo ""
    echo "📦 正在创建仓库..."
    
    if gh repo create ${REPO_NAME} --public --description "$REPO_DESC"; then
        echo "✅ 仓库创建成功"
        echo ""
        echo "📤 正在推送代码..."
        cd "/Users/hayha/Desktop/ios project"
        git push -u origin main
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "================================"
            echo "✅ 发布成功！"
            echo "================================"
            echo ""
            echo "🌐 仓库地址: https://github.com/${USERNAME}/${REPO_NAME}"
            echo ""
        fi
    else
        echo ""
        echo "❌ 仓库创建失败"
        echo ""
        echo "请手动创建仓库："
        echo "https://github.com/new?name=${REPO_NAME}&description=${REPO_DESC}&visibility=public"
        echo ""
        echo "创建后运行: git push -u origin main"
        echo ""
    fi
fi
