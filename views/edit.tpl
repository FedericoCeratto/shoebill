<!DOCTYPE HTML>
<html>
    <head>
        <title>Shoebill</title>
        <style>
            html, body {
                height: 100%;
                margin:0;
                padding:0;
                width: 100%;
                position:fixed;
            }
            html {
                font-size: 90%;
                position: relative;
            }
            body {
                background-color: #fafafa;
            }
            a {
                color: black;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }

            .leftcol {
                float: left;
                width: 14em;
                background: #923;
                height: 100%;
            }
            .centercol {
                float: left;
                width: 18em;
                height: 100%;
            }
            .rightcol {
                margin-left: 35em;
                height: 100%;
                padding: 1em;
            }

            div#buttons {
                padding: .5em;
            }
            div#buttons form  {
                text-align: center;
            }
            div#fsbox {
                padding: .5em 1em;
            }
            div#fsbox div {
                padding: 1%;
            }
            div#fsbox div#buttons {
                width: auto;
            }

            input#newfileinput {
                width: 10em;
            }

            input,textarea {
                border: 1px solid #dadada;
                margin-top: .5em;
                padding: .3em;
                -moz-border-radius: 5px;
                border-radius: 5px;
            }
            div#editform textarea {
                width: 100%;
                min-height: 30em;
                box-sizing:border-box;
            }

            span#savemsg {
                animation:msg_fadeout 5s;
                -webkit-animation:msg_fadeout 5s; /* Safari and Chrome */
                color: #fafafa;
            }
            @keyframes msg_fadeout
            {
                0%   {color:black;}
                100% {color:white;}
            }
            @-webkit-keyframes msg_fadeout /* Safari and Chrome */
            {
                0%   {color:black;}
                100% {color:white;}
            }

            .button {
                cursor: pointer;
                text-align: center;
                text-decoration: none;
                font-weight: bold;
                padding: .25em .8em;
                text-shadow: 0 1px 1px rgba(0,0,0,.3);
                -webkit-border-radius: .5em; 
                -moz-border-radius: .5em;
                border-radius: .5em;
                -webkit-box-shadow: 0 1px 2px rgba(0,0,0,.2);
                -moz-box-shadow: 0 1px 2px rgba(0,0,0,.2);
                color: #fef4e9;
                box-shadow: 0 1px 2px rgba(0,0,0,.2);
                border: solid 1px #da7c0c;
                background: #f78d1d;
                background: -webkit-gradient(linear, left top, left bottom, from(#faa51a), to(#f47a20));
                background: -moz-linear-gradient(top,  #faa51a,  #f47a20);
            }
            .button:hover {
                background: #f47c20;
                background: -webkit-gradient(linear, left top, left bottom, from(#f88e11), to(#f06015));
                background: -moz-linear-gradient(top,  #f88e11,  #f06015);
            }
            .centercol {
                -moz-box-shadow:    inset 0 -10px 10px #999;
                -webkit-box-shadow: inset 0 -10px 10px #999;
                box-shadow:         inset 0 -10px 10px #999;
            }
            div#pwchange {
                bottom: .7em;
                margin-left: 3em;
                position: absolute;
            }
            div#pwchange a { color: #ffe; }
        </style>


    </head>
    <body>
        <script type="text/javascript">
            function updateNewFileAction() {
                var path = document.getElementById('newfileform').action;
                var fname = document.getElementById("newfileinput").value;
                document.getElementById('newfileform').action = path + fname;
            }
        </script>


        <link rel="shortcut icon" href="/favicon.ico" />

        <div id="buttons" class="leftcol">
            <form action="/make/publish" method="POST">
                <input type="submit" class="button" value="Rebuild">
            </form>
        % for mt in make_targets:
            <form action="/make/{{mt}}" method="POST">
                <input type="submit" class="button" value="Make {{mt}}">
            </form>
        % end
            <form action="/logout" method="GET">
                <input type="submit" class="button" value="Logout">
            </form>
            % if aaa_enabled:
            <div id="pwchange">
                <a href="/change_password">Change password</a>
            </div>
            % end
        </div>

        <div id="fsbox" class="centercol">
            <p>Current directory:
                <a href="/edit/">(root)</a> /
                % url_chunks = path.url_chunks()
                % for n, chunk in enumerate(url_chunks[:-1]):
                    % url = '/'.join(url_chunks[:n+1])
                    <a href="/edit/{{url}}/">{{chunk}}</a> /
                % end
            </p>
            <div id="dirsbox">
                <p>Subdirectories:</p>
                % cwd_dirnames, cwd_filenames = path.list_current_dir()
                <ul>
                    % for i in cwd_dirnames:
                    <li>
                        <a href="/edit/{{i.as_url}}">{{i.basename()}}</a>
                    </li>
                    % end
                </ul>
            </div>
            <div id="filesbox">
                <p>Files:</p>
                <ul>
                    % for i in cwd_filenames:
                    <li>
                        <a href="/edit/{{i.as_url}}">{{i.basename()}}</a>
                    </li>
                    % end
                    <li>
                    % rel_url = path.basedir().as_url
                    % action_url = "/edit/%s/" % rel_url if rel_url else '/edit/'
                    <form id="newfileform" action="{{action_url}}" method="GET" onSubmit="updateNewFileAction();">
                        <label>
                            <input id="newfileinput" type="text">
                            <input type="submit" value="New file">
                        </label>
                    </form>
                    </li>
                </ul>
            </div>
        </div>

        <div id="editform" class="rightcol">
        % if not path.is_real_dir:
            <form action="/edit/{{path.as_url}}" method="POST">
                <textarea name="file_contents">{{contents}}</textarea>
                <br/>
                % if git_enabled:
                <label>Change description:<input type="text" name="desc"></label>
                % end
                <input type="submit" class="button" value="Save">
                % if savemsg:
                    <span id="savemsg">{{savemsg}}</span>
                % end
            </form>
        % end
        </div>

    </body>
</html>
