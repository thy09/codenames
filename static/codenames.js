var codenames = {
    load_words : function(words){
        for (var i=0;i<25;i++){
            var word = $("<div></div>").addClass("word").attr("id","w"+i).html("<p>"+words[i]+"</p>");
            $(".words").append(word);
        }
        $(".words").append($("<div style='clear:both'></div>"));
    },
    load_distribution: function(dist){
        for (var i=0;i<25;i++){
            $("#w"+i).addClass(dist[i]);
            var img_url = "./static/"+dist[i]+i%2+".jpg";
            if (dist[i] == 'x'){
                img_url = "./static/x.jpg";
            }
            $("#w"+i).append("<img src='"+img_url+"'></img>");
            var block = $("<div></div>").addClass("block "+dist[i]);
            $(".captain").append(block);
        }
        $(".captain").append($("<div style='clear:both'></div>"));
    },
    load_opened: function(opened){
        for (var i=0;i<25;i++){
            if (opened[i]){
                $("#w"+i).addClass("open");
            }else{
                $("#w"+i).removeClass("open");
            }
        }
    },
    load_game : function(game){
        this.load_words(game.words);
        this.load_distribution(game.dist);
        this.load_opened(game.opened);
        this.game = game;
        if (game.start == 'b'){
            $(".captain").addClass("b");
            $("#new_game").attr("href","/captain?start=r");
            $(".hint").append("<p>此轮游戏由蓝队先开始猜词</p>");
        }else{
            $("#new_game").attr("href","/captain?start=b");
            $(".hint").append("<p>此轮游戏由红队先开始猜词</p>");
        }
        for (var i=0;i<this.game.discussion.length;i++){
            $(".discussion").prepend("<p>"+unescape(this.game.discussion[i])+"</p>")
        }
    },
    sock_init : function(){
        this.sock.emit("join",{"id":this.game.id});
        this.sock.on("discussion", function(msg){
            console.log(msg);
            $(".discussion").prepend("<p>"+ unescape(msg.data) +"</p>");
        });
        this.sock.on("open", function(msg){
            console.log(msg);
            $("#w"+msg.data).addClass("open");
            codenames.game.opened[msg.idx] = 1;
        });
    },
    be_captain : function(){
        if (!confirm("确定是队长？队长会看到答案哦！")){
            return;
        }
        $(".word").addClass("show");
        $(".word").each(function(idx,elm){
            $(elm).click(function(){
                if (!confirm("确定点开 "+this.game.words[idx] + " 这个代号?")){
                    return;
                }
                this.game.opened[idx] = 1;
                var data = {"id":this.game.id,"idx":idx};
                this.sock.emit("open",{"data":data});
            }.bind(this));
        }.bind(this));
        $(".captain").removeClass("hidden");
    },
    submit : function(){
        var name = $("#name").val();
        var sentence = $("#sentence").val();
        if (name == ""){
            alert("请输入姓名");
            return;
        }
        if (sentence == ""){
            alert("请输入发言");
            return;
        }
        var data = {"id":this.game.id,"say":escape(name+": "+sentence)};
        console.log(data);
        this.sock.emit("update",{"data":data});
        $("#sentence").val("");
    },
    sock : null,
}
