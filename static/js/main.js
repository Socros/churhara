document.querySelectorAll("input[type='checkbox']").forEach(function(cbx){
    cbx.addEventListener('change',function(){
        let id = this.dataset.id;
        window.location.href = `/toggle/${id}`;
    })
})


