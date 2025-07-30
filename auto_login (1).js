const axios = require('axios');
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
        const response = await axios.post(config.apiUrl, {
            cmd: 'login',
            id_mobile: config.username,
            password: config.password
        });

        // 检查响应状态
        if (response.status === 200) {
            // 处理登录成功逻辑
            console.log('登录成功');
            console.log('响应数据:', response.data);
            
            // 保存cookie或token等信息
            // const cookies = response.headers['set-cookie'];
            // console.log('获取到的Cookie:', cookies);
            
            await notify.sendNotify('登录成功', '已成功登录到指定网站');
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
    