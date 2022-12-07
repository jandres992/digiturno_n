function notificacion(ind,aviso) {
    if (ind == 1) {
        var type = 'info';
    } else if (ind == 2) {
        var type = 'success';
    } else if (ind == 0) {
        var type = 'danger';
    }
    $.notify({
        icon: 'fa fa-info-circle',
        message: "<strong>" + aviso + "</strong> ",
    }, {
        type: type,
        animate: {
            enter: 'animated bounceInDown',
            exit: 'animated bounceOutUp'
        },
        placement: {
            from: "top",
            align: "center"
        }
    });
}