$(document).ready(function(){
var codelec = $('#cod').val();
    getJsonElectors(codelec);
});


function getJsonElectors(codelec){



$.ajax({

    url:"http://127.0.0.1:8000/district-electors/"+codelec,
    method: 'GET',
    success:function(result){
        console.log(result[0]);
        $('#tb_electors').DataTable({
            data: result,
            columns:[
                {"data":"idCard"},
                {"data":"fullName"},
                {"data":"gender"}
            ]
        })

    },
    error: function(){
        console.log("Error retreiving data from "+codelec);
    }

});

}