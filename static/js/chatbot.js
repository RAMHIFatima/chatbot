$(document).ready(function() {
	$('#chat').submit(function(event){
		
  	event.preventDefault();
	var form = $(this);
	var num = form.find('input').val();
  if (num){
  		
			$.ajax({
				method: 'POST',
				url: form.attr('action'),
				data: form.serialize(),
				beforeSend: function() {
				},
				success: function(data) {
					var number=data.number;
					var story =data.story;
					var $div ='';
					form.parent().parent().append(data);
					form.parent().addClass('d-none');// remove the form from the 
					submitFormChatbot();
				},
				error: function(data) {	},
				complete: function(data) {
        				}
			});

	 }
	});

	
});

function formatDate()
{
	n =  new Date();
    y = n.getFullYear();
    m = n.getMonth() + 1;
    d = n.getDate();
    h =n.getHours();
    min =n.getMinutes();
    return d + "/" + m + "/" + y+ " " + h + ":" + min;
}

function submitFormChatbot()
{
	$('#chatForm').submit(function(event) {
		event.preventDefault();
		var form = $(this);
		var question = form.find('input').val();
		var $imge='<div class="incoming_msg_img"><img src="static/img/profile.png" alt="bot"/></div>';
		if (question){
			$.ajax({
				method: 'POST',
				url: form.attr('action'),
				data: form.serialize(),
				beforeSend: function() {
    				$('.msg_send_btn').attr('disabled', true);
	    			var $questionTemplate = '<div class="outgoing_msg"><div class="sent_msg">' +
	    			'<p>' + question + '</p><span class="time_date">' + formatDate() + '</span></div></div>';
					$('.msg_history').append($questionTemplate);
					form.find('input').val('');
				},
				success: function(data) {
					console.log(data);
					var name=data.name;
					var prediction =data.pred;
					var error= data.error;
					
					if (error){
						var $questionTemplate =$imge+'<div class="received_msg"><div class="received_withd_msg">'+'<p>'+error+
		                '</p>'+'<span id="date"class="time_date">' + formatDate() +'</span></div></div>';
					}
					else{
						var $questionTemplate = $imge+'<div class="received_msg"><div class="received_withd_msg">'+'<p>'+name+' is in the '+prediction+
		                '</p>'+'<span id="date"class="time_date">' + formatDate() +'</span></div></div>';
					
					}	
					$('.msg_history').append($questionTemplate);
				},
				error: function(data) {
					console.log(data);
					var $questionTemplate = $imge+'<div class="received_msg"><div class="received_withd_msg">'+'<p> Sorry!I dit not understand your demand. Please enter a question based on the story ! </p>'+
	                '<span id="date"class="time_date">' + formatDate() +'</span></div></div>';
					$('.msg_history').append($questionTemplate);
				},
				complete: function(data) {
					console.log(data);
        			$('.msg_send_btn').attr('disabled', false);
        			var objDiv = document.getElementById("scroll");
					objDiv.scrollTop = objDiv.scrollHeight;
				}
			});

	 }

	});
}