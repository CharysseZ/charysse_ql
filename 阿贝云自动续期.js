// cron: 1 0 0 * * *
// new Env('阿贝云自动续期');

const axios = require('axios');
const querystring = require('querystring'); // 使用Node.js内置模块
const notify = require('./sendNotify'); // 引入青龙通知模块

// 从环境变量获取配置信息
const config = {
    apiUrl: 'https://api.abeiyun.com/www/login.php',
    username: process.env.aby_username || '',      // 从环境变量获取用户名
    password: process.env.aby_password || '',      // 从环境变量获取密码
    isEnabled: true    // 是否启用脚本
};

// 登录函数
async function login() {
    if (!config.isEnabled) {
        console.log('脚本未启用，跳过执行');
        return;
    }

    if (!config.username || !config.password) {
        console.log('请配置环境变量 aby_username 和 aby_password');
        await notify.sendNotify('登录失败', '请在青龙面板环境变量中配置 aby_username 和 aby_password');
        return;
    }

    try {
        // 准备表单数据
        const formData = {
            cmd: 'login',
            id_mobile: config.username,
            password: config.password
        };

        const response = await axios.post(config.apiUrl, 
            querystring.stringify(formData), // 使用内置模块转换为表单格式
            {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded' // 设置表单提交的Content-Type
                }
            }
        );

        // 检查响应状态
        if (response.status === 200) {
            // 处理空响应
            if (response.data === '' || response.data === null) {
                console.log('登录失败：服务器返回空数据');
                await notify.sendNotify('登录失败', '服务器返回空数据，请检查登录信息');
                return;
            }
            
            // 尝试解析响应数据（可能是JSON或其他格式）
            let data;
            try {
                // 尝试解析为JSON
                data = typeof response.data === 'string' ? JSON.parse(response.data) : response.data;
            } catch (parseError) {
                // 如果解析JSON失败，直接使用原始数据
                console.log('登录响应不是JSON格式:', response.data);
                data = { msg: response.data };
            }
            
            // 输出完整响应数据用于调试（已修正语法错误）
            console.log('完整响应数据:', JSON.stringify(data, null, 2));
            
            // 先检查是否为成功状态
            if ((data.response === "200" && data.msg?.includes("登录成功")) || 
                (data.msg && data.msg.includes("登录成功"))) {
                console.log('登录成功');
                await notify.sendNotify('登录成功', '已成功登录到阿贝云');
                return;
            }
            
            // 通用错误处理 - 非200状态码
            if (data.response && data.response !== "200") {
                let errorMsg = `错误代码: ${data.response}`;
                if (data.msg) {
                    errorMsg += `，信息: ${data.msg}`;
                    
                    // 识别常见错误类型
                    if (data.msg.includes('密码') || (data.response === '500103')) {
                        errorMsg = '密码输入错误';
                    } else if (data.msg.includes('手机号') || data.msg.includes('账户') || (data.response === '500101')) {
                        errorMsg = '手机号或账户输入错误';
                    }
                }
                
                console.log(`登录失败：${errorMsg}`);
                await notify.sendNotify('登录失败', errorMsg);
                return;
            }
            
            // 处理没有状态码但有错误信息的情况
            if (data.msg && !data.msg.includes('登录成功')) {
                console.log(`登录失败：${data.msg}`);
                await notify.sendNotify('登录失败', data.msg);
                return;
            }
            
            // 所有条件都不匹配的情况
            console.log('登录失败：未知响应格式');
            await notify.sendNotify('登录失败', '未知响应格式，请查看日志详情');
            
        } else {
            console.log(`登录失败，状态码: ${response.status}`);
            await notify.sendNotify('登录失败', `状态码: ${response.status}`);
        }
    } catch (error) {
        console.error('登录过程中发生错误:', error.message);
        if (error.response) {
            console.error('错误响应数据:', error.response.data);
            console.error('错误响应状态:', error.response.status);
        }
        await notify.sendNotify('登录错误', error.message);
    }
}

// 执行登录
login().catch(console.error);        
