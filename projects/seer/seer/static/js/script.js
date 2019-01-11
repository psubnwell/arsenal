$(document).ready(function () {

    // Bind a callback that executes when document.location.hash changes.
    $(window).bind('hashchange', function () {
        // 有些浏览器不返回#, 这里统一去掉#
        var hash = window.location.hash.replace('#', '');
        var url = null;
        var methodName = null;
        // 根据hash值的不同, 选择对应的页面URL
        // 这些变量存储对应页面的URL, 在根页面定义
        switch (hash) {
        case 'network_visualize':
            url = network_visualize_url;
            methodName = '传播网络分析';
            break;
        case 'reports_track':
            url = reports_track_url;
            methodName = '权威报道跟踪';
            break;
        }
        // 向对应的页面URL发送GET请求, 服务器端会返回对应的局部模板
        $.ajax({
            type: 'GET',
            url: url,
            success: function (data) {
                $('#analysis-method').text(methodName);
                plot(method=hash, data=data, elementID='analysis-content');
            }
        });
    });

    // 代码初始化程序
    if (window.location.hash != '') {
        $(window).trigger('hashchange');
    }
});
