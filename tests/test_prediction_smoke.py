import io
import importlib
import sys
import types

from fastapi.testclient import TestClient


class DummyNetworkModel:
    def predict(self, dataframe):
        return [1] * len(dataframe)


def test_predict_route_returns_html_table(monkeypatch):
    sys.modules.setdefault("pymongo", types.SimpleNamespace(MongoClient=object))
    sys.modules.setdefault("dagshub", types.SimpleNamespace(init=lambda **kwargs: None))

    app_module = importlib.import_module("app")
    monkeypatch.setattr(app_module, "load_network_model", lambda: DummyNetworkModel())

    with TestClient(app_module.app) as client:
        file_content = io.BytesIO(
            b"having_IP_Address,URL_Length,Shortining_Service,having_At_Symbol,double_slash_redirecting,Prefix_Suffix,having_Sub_Domain,SSLfinal_State,Domain_registeration_length,Favicon,port,HTTPS_token,Request_URL,URL_of_Anchor,Links_in_tags,SFH,Submitting_to_email,Abnormal_URL,Redirect,on_mouseover,RightClick,popUpWidnow,Iframe,age_of_domain,DNSRecord,web_traffic,Page_Rank,Google_Index,Links_pointing_to_page,Statistical_report\n-1,1,1,1,-1,-1,-1,-1,-1,1,1,-1,1,-1,1,-1,-1,-1,0,1,1,1,1,-1,-1,-1,-1,1,1,-1\n"
        )
        response = client.post(
            "/predict",
            files={"file": ("sample.csv", file_content, "text/csv")},
        )

    assert response.status_code == 200
    assert "Predicted Data" in response.text
    assert "predicted_column" in response.text
