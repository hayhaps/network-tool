#!/bin/bash
# 使用GitHub API创建仓库

echo "================================"
echo "🚀 GitHub仓库创建脚本"
echo "================================"
echo ""

# 检查是否提供了GitHub Token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  需要GitHub Token才能创建仓库"
    echo ""
    echo "获取Token的步骤："
    echo "1. 访问 https://github.com/settings/tokens"
    echo "2. 点击 'Generate new token (classic)'"
    echo "3. 勾选 'repo' 权限"
    echo "4. 生成Token并复制"
    echo ""
    read -p "请输入你的GitHub Token: " TOKEN
    export GITHUB_TOKEN=$TOKEN
fi

echo "📦 正在创建GitHub仓库..."

# 创建仓库
RESPONSE=$(curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{
    "name": "network-diagnostic-tool",
    "description": "网络故障排查工具 - 功能全面的网络诊断工具",
    "private": false,
    "auto_init": false
  }')

# 检查响应
if echo "$RESPONSE" | grep -q '"id":'; then
    echo "✅ 仓库创建成功！"
    echo ""
    echo "🌐 仓库地址: https://github.com/hayha/network-diagnostic-tool"
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
        echo "🎉 你的项目已成功发布到GitHub！"
        echo ""
        echo "📎 仓库链接: https://github.com/hayha/network-diagnostic-tool"
        echo ""
    else
        echo ""
        echo "❌ 推送失败"
        echo "请检查网络连接或认证信息"
    fi
else
    echo "❌ 仓库创建失败"
    echo ""
    echo "错误信息:"
    echo "$RESPONSE" | grep -o '"message":"[^"]*"'
    echo ""
    echo "可能的原因："
    echo "1. Token无效或已过期"
    echo "2. 仓库名称已存在"
    echo "3. 网络连接问题"
fi
