$('#search-button').click(function(){
    $('.cont-tournament').show();

    var value = $("#my-search").val().toLowerCase();
    $(".header h2").filter(function(){
        if(!$(this.parentNode.parentNode).is(":hidden")){
            $(this.parentNode.parentNode).toggle($(this).text().toLowerCase().indexOf(value) > -1);
        }
    });
});


function check_submit(){
    var name = document.getElementById("tournament_form_name").value;
    if(name==''){
        alert("Please set a name of a tournament");
    }
    else{
        var date = document.getElementById("tournament_date").value;
        if (date == ''){
            alert("Please set a date of a tournament");
        }
        else {
            var deadline = document.getElementById("deadline_date").value;
            if (deadline == ''){
                alert("Please set a deadline of registration");
            }
            else{
                console.log(Date.parse(deadline))
                console.log(Date.parse(date))
                if(Date.parse(deadline) > Date.parse(date)){
                    alert("Deadline date should not be later that the actual date of the tournament");
                }
                else{
                    var UserDate = document.getElementById("tournament_date").value;
                    var ToDate = new Date();

                    if (new Date(UserDate).getTime() < ToDate.getTime()) {
                      alert("Date from the past cannot be set");
                     }
                     else{
                        var UserDate = document.getElementById("deadline_date").value;
                        var ToDate = new Date();

                        if (new Date(UserDate).getTime() < ToDate.getTime()) {
                              alert("Date from the past cannot be set");
                         }
                         else{
                            var limit = document.getElementById("limit").value;
                            var seeded = document.getElementById("seeded").value;
                            console.log(limit);
                            console.log(seeded);
                            if(parseInt(limit) < parseInt(seeded)){
                                alert("Number of seeded participants cannot be greater than maximum number of participants")
                            }
                            else{
                                return confirm('Are you sure?');
                            }
                         }
                     }
                }
            }
        }
    }
    return false;
};



submitForms = function(){
    document.getElementById("result-form").submit();
    document.getElementById("match-form").submit();
}