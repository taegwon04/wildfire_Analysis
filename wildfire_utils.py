from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from IPython.display import display, Markdown, HTML
import ipywidgets as widgets
import pandas as pd

# 모델 정의
model_options = {
    "랜덤 포레스트": RandomForestClassifier(n_estimators=100),
    "로지스틱 회귀": LogisticRegression(max_iter=1000),
    "신경망 (MLP)": MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500)
}

# 학습 함수
def train_model(model, X, y):
    # NaN 제거
    df_clean = pd.concat([X, y], axis=1).dropna()
    X_clean = df_clean.iloc[:, :-1]
    y_clean = df_clean.iloc[:, -1]

    X_train, X_test, y_train, y_test = train_test_split(X_clean, y_clean, test_size=0.3, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    return model, acc, report

# 리포트 출력
def show_report(acc, report):
    display(Markdown(f"### ✅ 정확도: **{acc * 100:.1f}%**"))
    display(Markdown("**클래스별 F1-score:**"))
    for label in ['0', '1']:
        if label in report:
            f1 = report[label]['f1-score']
            display(Markdown(f"- 클래스 {label}: F1 = {f1:.2f}"))

# 예측 위젯
def prediction_ui(model, selected_features):
    sliders = {}
    for col in selected_features:
        sliders[col] = widgets.FloatSlider(description=col, min=0, max=100, step=1)
        display(sliders[col])

    button = widgets.Button(description="🔥 예측")
    output = widgets.Output()

    def on_click(b):
        row = [[sliders[col].value for col in selected_features]]
        df = pd.DataFrame(row, columns=selected_features)
        prob = model.predict_proba(df)[0][1]
        with output:
            output.clear_output()
            display(Markdown(f"### 🔥 산불 대형화 확률: **{prob * 100:.1f}%**"))

    button.on_click(on_click)
    display(button, output)

# 학생용 인터페이스
def start_student_interface(df):
    feature_options = ['Temp_pre_7', 'Hum_pre_7', 'Wind_pre_7', 'Prec_pre_7', 'remoteness']

    feature_selector = widgets.SelectMultiple(
        options=feature_options,
        value=('Temp_pre_7', 'Wind_pre_7', 'remoteness'),
        description='📊 변수선택 (3개):',
        rows=5,
        style={'description_width': '150px'},
        layout=widgets.Layout(width='400px')
    )

    model_radio = widgets.RadioButtons(
        options=list(model_options.keys()),
        description='🤖 모델:',
        style={'description_width': '80px'}
    )

    run_button = widgets.Button(description="🚀 모델 학습 및 평가", button_style='success')
    output = widgets.Output()

    def run_model(b):
        with output:
            output.clear_output()
            selected = list(feature_selector.value)
            if len(selected) != 3:
                print("⚠️ 변수는 정확히 3개 선택해야 합니다.")
                return

            model_name = model_radio.value
            model = model_options[model_name]

            X = df[selected]
            y = df['large_fire']

            model, acc, report = train_model(model, X, y)
            show_report(acc, report)
            prediction_ui(model, selected)

    run_button.on_click(run_model)

    display(widgets.VBox([
        widgets.Label("🔧 산불 예측 모델 만들기 실험 키트"),
        feature_selector,
        model_radio,
        run_button,
        output
    ]))
