#!/bin/bash
# GitHub发布完整解决方案

echo "================================"
echo "🚀 GitHub发布解决方案"
echo "================================"
echo ""

echo "📋 当前状态："
echo "   - 组织仓库: liweihay-dev/network-diagnostic-tool (存在，但无权限)"
echo "   - 个人仓库: hayhaps/network-diagnostic-tool (不存在)"
echo ""

echo "请选择方案："
echo ""
echo "1️⃣  在个人账号创建新仓库"
echo "   访问: https://github.com/new"
echo "   仓库名: network-diagnostic-tool"
echo "   创建后运行: git push -u origin main"
echo ""

echo "2️⃣  使用Token推送到组织仓库"
echo "   需要提供GitHub Token"
echo ""

echo "3️⃣  申请组织仓库权限"
echo "   联系 liweihay-dev 管理员"
echo ""

read -p "请选择方案 (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo "📦 正在打开GitHub创建页面..."
        if command -v open &> /dev/null; then
            open "https://github.com/new?name=network-diagnostic-tool&description=网络故障排查工具%20-%20功能全面的网络诊断工具&visibility=public"
        else
            echo "请访问: https://github.com/new?name=network-diagnostic-tool&description=网络故障排查工具%20-%20功能全面的网络诊断工具&visibility=public"
        fi
        echo ""
        echo "创建完成后，运行: git push -u origin main"
        ;;
    2)
        echo ""
        read -p "请输入GitHub Token: " token
        if [ -n "$token" ]; then
            cd "/Users/hayha/Desktop/ios project"
            git remote remove origin
            git remote add origin https://$token@github.com/liweihay-dev/network-diagnostic-tool.git
            git push -u origin main
        fi
        ;;
    3)
        echo ""
        echo "请访问: https://github.com/liweihay-dev/network-diagnostic-tool/settings/collaboration"
        echo "申请仓库写入权限"
        ;;
    *)
        echo "无效选择"
        ;;
esac
