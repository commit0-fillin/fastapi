import json
from typing import Any, Dict, Optional
from fastapi.encoders import jsonable_encoder
from starlette.responses import HTMLResponse
from typing_extensions import Annotated, Doc
swagger_ui_default_parameters: Annotated[Dict[str, Any], Doc('\n        Default configurations for Swagger UI.\n\n        You can use it as a template to add any other configurations needed.\n        ')] = {'dom_id': '#swagger-ui', 'layout': 'BaseLayout', 'deepLinking': True, 'showExtensions': True, 'showCommonExtensions': True}

def get_swagger_ui_html(*, openapi_url: Annotated[str, Doc('\n            The OpenAPI URL that Swagger UI should load and use.\n\n            This is normally done automatically by FastAPI using the default URL\n            `/openapi.json`.\n            ')], title: Annotated[str, Doc('\n            The HTML `<title>` content, normally shown in the browser tab.\n            ')], swagger_js_url: Annotated[str, Doc('\n            The URL to use to load the Swagger UI JavaScript.\n\n            It is normally set to a CDN URL.\n            ')]='https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js', swagger_css_url: Annotated[str, Doc('\n            The URL to use to load the Swagger UI CSS.\n\n            It is normally set to a CDN URL.\n            ')]='https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css', swagger_favicon_url: Annotated[str, Doc('\n            The URL of the favicon to use. It is normally shown in the browser tab.\n            ')]='https://fastapi.tiangolo.com/img/favicon.png', oauth2_redirect_url: Annotated[Optional[str], Doc('\n            The OAuth2 redirect URL, it is normally automatically handled by FastAPI.\n            ')]=None, init_oauth: Annotated[Optional[Dict[str, Any]], Doc('\n            A dictionary with Swagger UI OAuth2 initialization configurations.\n            ')]=None, swagger_ui_parameters: Annotated[Optional[Dict[str, Any]], Doc('\n            Configuration parameters for Swagger UI.\n\n            It defaults to [swagger_ui_default_parameters][fastapi.openapi.docs.swagger_ui_default_parameters].\n            ')]=None) -> HTMLResponse:
    """
    Generate and return the HTML  that loads Swagger UI for the interactive
    API docs (normally served at `/docs`).

    You would only call this function yourself if you needed to override some parts,
    for example the URLs to use to load Swagger UI's JavaScript and CSS.

    Read more about it in the
    [FastAPI docs for Configure Swagger UI](https://fastapi.tiangolo.com/how-to/configure-swagger-ui/)
    and the [FastAPI docs for Custom Docs UI Static Assets (Self-Hosting)](https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/).
    """
    current_swagger_ui_parameters = swagger_ui_default_parameters.copy()
    if swagger_ui_parameters:
        current_swagger_ui_parameters.update(swagger_ui_parameters)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link type="text/css" rel="stylesheet" href="{swagger_css_url}">
    <link rel="shortcut icon" href="{swagger_favicon_url}">
    <title>{title}</title>
    </head>
    <body>
    <div id="swagger-ui">
    </div>
    <script src="{swagger_js_url}"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({{
        url: '{openapi_url}',
        {json.dumps(current_swagger_ui_parameters)[1:-1]}
        presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
        {f'oauth2RedirectUrl: "{oauth2_redirect_url}",' if oauth2_redirect_url else ""}
    }})
    {f"ui.initOAuth({json.dumps(init_oauth)})" if init_oauth else ""}
    </script>
    </body>
    </html>
    """
    return HTMLResponse(html)

def get_redoc_html(*, openapi_url: Annotated[str, Doc('\n            The OpenAPI URL that ReDoc should load and use.\n\n            This is normally done automatically by FastAPI using the default URL\n            `/openapi.json`.\n            ')], title: Annotated[str, Doc('\n            The HTML `<title>` content, normally shown in the browser tab.\n            ')], redoc_js_url: Annotated[str, Doc('\n            The URL to use to load the ReDoc JavaScript.\n\n            It is normally set to a CDN URL.\n            ')]='https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js', redoc_favicon_url: Annotated[str, Doc('\n            The URL of the favicon to use. It is normally shown in the browser tab.\n            ')]='https://fastapi.tiangolo.com/img/favicon.png', with_google_fonts: Annotated[bool, Doc('\n            Load and use Google Fonts.\n            ')]=True) -> HTMLResponse:
    """
    Generate and return the HTML response that loads ReDoc for the alternative
    API docs (normally served at `/redoc`).

    You would only call this function yourself if you needed to override some parts,
    for example the URLs to use to load ReDoc's JavaScript and CSS.

    Read more about it in the
    [FastAPI docs for Custom Docs UI Static Assets (Self-Hosting)](https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/).
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <title>{title}</title>
    <!-- needed for adaptive design -->
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    """
    if with_google_fonts:
        html += """
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    """
    html += f"""
    <link rel="shortcut icon" href="{redoc_favicon_url}">
    <!--
    ReDoc doesn't change outer page styles
    -->
    <style>
      body {{
        margin: 0;
        padding: 0;
      }}
    </style>
    </head>
    <body>
    <redoc spec-url="{openapi_url}"></redoc>
    <script src="{redoc_js_url}"> </script>
    </body>
    </html>
    """
    return HTMLResponse(html)

def get_swagger_ui_oauth2_redirect_html() -> HTMLResponse:
    """
    Generate the HTML response with the OAuth2 redirection for Swagger UI.

    You normally don't need to use or change this.
    """
    html = """
    <!DOCTYPE html>
    <html lang="en-US">
    <body onload="run()">
    </body>
    </html>
    <script>
        'use strict';
        function run () {
            var oauth2 = window.opener.swaggerUIRedirectOauth2;
            var sentState = oauth2.state;
            var redirectUrl = oauth2.redirectUrl;
            var isValid, qp, arr;

            if (/code|token|error/.test(window.location.hash)) {
                qp = window.location.hash.substring(1);
            } else {
                qp = location.search.substring(1);
            }

            arr = qp.split("&");
            arr.forEach(function (v,i,_arr) { _arr[i] = '"' + v.replace('=', '":"') + '"';});
            qp = qp ? JSON.parse('{' + arr.join() + '}',
                    function (key, value) {
                        return key === "" ? value : decodeURIComponent(value);
                    }
            ) : {};

            isValid = qp.state === sentState;

            if ((
            oauth2.auth.schema.get("flow") === "accessCode" ||
            oauth2.auth.schema.get("flow") === "authorizationCode" ||
            oauth2.auth.schema.get("type") === "oauth2") && !oauth2.auth.code) {
                if (!isValid) {
                    oauth2.errCb({
                        authId: oauth2.auth.name,
                        source: "auth",
                        level: "warning",
                        message: "Authorization may be unsafe, passed state was changed in server Passed state wasn't returned from auth server"
                    });
                }

                if (qp.code) {
                    delete oauth2.state;
                    oauth2.auth.code = qp.code;
                    oauth2.callback({auth: oauth2.auth, redirectUrl: redirectUrl});
                } else {
                    let oauthErrorMsg;
                    if (qp.error) {
                        oauthErrorMsg = "["+qp.error+"]: " +
                            (qp.error_description ? qp.error_description+ ". " : "no accessCode received from the server. ") +
                            (qp.error_uri ? "More info: "+qp.error_uri : "");
                    }

                    oauth2.errCb({
                        authId: oauth2.auth.name,
                        source: "auth",
                        level: "error",
                        message: oauthErrorMsg || "[Authorization failed]: no accessCode received from the server"
                    });
                }
            } else {
                oauth2.callback({auth: oauth2.auth, token: qp, isValid: isValid, redirectUrl: redirectUrl});
            }
            window.close();
        }
    </script>
    """
    return HTMLResponse(content=html)
