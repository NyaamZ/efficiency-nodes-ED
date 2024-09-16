✨🍬Efficiency Nodes for ComfyUI Version 2.0+ 에서 다양한 기능을 추가한 포크 버전. 원본의 설명은 https://github.com/jags111/efficiency-nodes-comfyui 를 참조.🍬


<b> Efficiency Nodes 💬ED (V6)
=======
### 워크플로 (EXIF 있음):
<p align="left">
  <img src="https://github.com/user-attachments/assets/22246adb-ab46-48ae-ad57-58206d98630e" width="800" style="display: inline-block;">
</p>
원본과 다르게 💬ED노드는 Context 링크를 주고 받는다.<br>
&nbsp;&nbsp;&nbsp;&nbsp;-( 오른쪽 아래에 BiRefNet이 포함되어 있다. 필요없으면 워크플로에서 삭제하자.<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;BiRefNet은 필요없는 배경을 삭제하는데 정말 좋은 도구이다. 한번 써보는 것을 추천)<br>

### Context:
<p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/1c55eecb-7c9d-402d-bf3d-9ecb4c109d3d" width="600" style="display: inline-block;">
</p>
context를 사용해 어지럽게 널린 링크들을 위의 그림 처럼 단 한개로 정리했다!<br><br>
context는 model, clip, vae, positve 컨디셔닝, negative 컨디셔닝, 등등이 합쳐져 있는 코드 다발로 생각하면 된다.<br>
(rgthree의 커스텀 노드에서 차용)<br>
Efficiency Nodes 💬ED의 context는 rgthree의 노드가 없어도 독립적으로 작동하지만 rgthree의 커스텀 노드 설치를 권장한다. 당연하지만 rgthree의 context와 호환된다.<br><br>
<details>
  <summary><b>context 간단 사용법</b></summary>
<ul>
<p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/cf795977-8ab6-4646-9d28-02737122cd88" width="300" style="display: inline-block;"><br>
  context에서 특정한 요소를 추출하려면 위의 그림처럼 rgthree의 context 노드로 추출할 수 있다.</p>
<p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/d82d0bd1-45fc-4f72-8cd8-15b61693db8c" width="300" style="display: inline-block;"><br>
  context에 특정한 요소를 입력하려면 위의 그림처럼 하면된다.</p>
</ul></details>

### 추가한 💬ED 노드:
<!-------------------------------------------------------------------------------------------------------------------------------------------------------->
<details>
    <summary><b>Efficient Loader 💬ED</b></summary>
<ul>
    <p></p>
    <li>클릭 한번으로 Txt2Img, Img2Img, Inpaint 모드 설정이 가능하다.<br><i>(Txt2Img로 설정시 처음에 연결된 Ksampler (Efficient) 💬ED의 denoise 값이 자동으로 1로 설정됨.)</i><br>
      <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/0f8549b8-cbe0-4662-b922-df21545e2d8f" width="250" style="display: inline-block;">
      </li>
    <p></p>
    <li>Inpaint(MaskDetailer) 모드가 추가 되었다.<br><i>(그냥 Inpaint를 사용하면 점점 화질이 열화되는데 Impact Pack의 MaskDetailer를 임포트 시켰다.</i><br>
      <i>자세한 것은 Inpaint(MaskDetailer)에서 설명.)</i><br>
      <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/5b04b764-f995-4350-b897-e42041686a2d" width="250" style="display: inline-block;">
      </li>
    <li>seed, cfg, sampler, scheduler를 설정하고 <code>context</code>에 저장. 후에 Ksampler (Efficient) 💬ED등에서 그 설정값을 이용할 수 있다.</li>
    <p></p>
    <li>오른 클릭에 드롭다운 메뉴 추가.<br>
        <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/47995eca-94fb-4e52-b77b-2a53e9f292d0" width="150" style="display: inline-block;">
        <p> "🔍 View model info..."는 모델의 정보를 표시한다.<br>          
          <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/f7cf378c-cd8a-49cb-9389-5681caacf130" width="250" style="display: inline-block;"><br>
          <i>("🔍 View model info..."는 크기가 큰 모델은 해쉬값을 찾느라 '첫' 로딩이 느리다. 처음 한번은 "Use as preview"를 눌러 주는걸 권장.)</i><br></p>
        <p> "📐 Aspect Ratio..."는 image_width와 image_height에 선택한 값을 입력한다.<br>
          <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/f92fdd33-ddcb-4b42-904c-4c67a52e4aa0" width="250" style="display: inline-block;"><br>
          <i>(Txt2Img 모드로 이미지를 만들 때 편리하다. ◆ 표시는 추천 해상도)</i><br></p>
    </li>
    <li>모델 선택시 프리뷰 이미지 표시<br>
        <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/9ff41533-ba10-4707-a61b-61167aea23a9" width="250" style="display: inline-block;"><br>
          <i>(이름 입력 창은 하위 폴더별로 서브메뉴가 만들어지며 "🔍 View model info..."에서 "Use as preview"했던 이미지를 모델 선택시 보여준다.</i><br>
          <i>모델의 프리뷰 이미지가 있다면 이름 옆에 '*'로 표시된다.</i><br>
          <i>폴더와 모델이 함께 있을땐 유형 별로 정렬이 안되는데 그땐 폴더 이름 맨 앞에 <code>-</code>를 붙여주면 정렬이 된다.)</i><br>
    </li>
    <p></p>
    <li>Tiled VAE 인코딩<br>
        <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/b160f24f-09f6-460f-a1a4-e906077ff61b" width="300" style="display: inline-block;"><br>
          - 오른 클릭 > Property Panel에서 Use tiled VAE encode를 true로 하면 VAE 인코딩시에 Tiled VAE 인코딩을 사용한다.<br>
          - Tiled VAE 인코딩은 큰 이미지를 VRAM이 부족해도 인코딩할 수 있다. 대신 기본보다 느리다.<br>
    </li>
    <p></p>
    <li>로라, 임베딩, 컨트롤 넷 스태커를 <code>lora_stack</code>과 <code>cnet_stack</code>에 입력 가능.</li>
    <p></p>
    <li>positive와 negative 프롬프트 텍스트 박스 내장. <code>token_normalization</code>과 <code>weight_interpretation</code>에서 프롬프트 <a href="https://github.com/BlenderNeko/ComfyUI_ADV_CLIP_emb">인코딩</a> 방식 설정 가능.</li>
    <p></p>
    <li>Efficient Loader 💬ED에서 context로 출력하는 값은: model, clip, vae, positive, negative, latent, images, seed, cfg, sampler, scheduler, clip_width=image_width, clip_height=image_height, text_pos_g=positive_text, text_neg_g=negative_text 이다.</li>
</ul>
</details>
<!-------------------------------------------------------------------------------------------------------------------------------------------------------->
<details>
    <summary><b>KSampler (Efficient) 💬ED</b>, <b>KSampler TEXT (Eff.) 💬ED</b></summary>
<p></p>
- 원래 에피션트 노드에서 context를 입력 받을 수 있게 수정.<p></p>
- 이미지를 샘플링 후 context와 OUTPUT_IMAGE에 출력한다. SOURCE_IMAGE는 입력받은 이미지.<p></p>
- KSampler TEXT (Eff.) 💬ED는 배경 제작용으로 따로 프롬프트 텍스트 입력창을 추가한 버전.<br>
  (KSampler TEXT (Eff.) 💬ED가 생성하는 이미지 사이즈는 image_source_to_use로 선택에 따라 context의 이미지 또는 latent를 참조하고 텍스트 입력창의 프롬프트 텍스트는 context에 저장하지 않는다.)
<p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/37ca01cb-0b8e-4e14-9d86-7dcf09c3a481" width="500">
</p>
    <p></p>
    <li>set_seed_cfg_sampler 설정으로 context에서 seed, cfg, sampler, scheduler 설정을 가져오기 또는 내보내기가 가능<br>
      <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/57694db3-b520-47ef-b401-8fcbfd1eb63b" width="250" style="display: inline-block;"><br>
      - from node to ctx는 현재 노드의 seed, cfg, sampler, scheduler 설정을 context에 내보내기<br>
      - from context는 context에서 seed, cfg, sampler, scheduler 설정을 가져오기<br>
      - from node only는 현재 노드의 seed, cfg, sampler, scheduler 설정을 이용하고 context에 저장하지는 않는다.<br>
    </li>    
    <p></p>
    <li>VAE decode 설정<br
      - 샘플링 후 이미지 생성을 위한 vae 디코딩시에 무엇을 사용할지 선택할 수 있다.<br>
      - Properties Panel에서 Use tiled VAE decode를 true로 하면 된다.<br>
      - Tiled VAE 디코딩은 큰 이미지를 VRAM이 부족해도 디코딩할 수 있다. 대신 기본보다 느리다.
    </li>
</details>
<!-------------------------------------------------------------------------------------------------------------------------------------------------------->
<details>
    <summary><b>Inpaint(MaskDetailer) 모드</b></summary>
<p></p>
- Efficient Loader 💬ED에서 Inpaint(MaskDetailer) 모드를 선택하면 에피션트 샘플러 💬ED가 마스크 디테일러 모드로 변경된다.<p></p>
- Impact Pack의 MaskDetailer를 그대로 통합시켰다.<p></p>
- 인페인트에 정말 탁월하고 화질의 열화가 일어나지 않는다.<br>
  (사용법은 기존의 MaskDetailer와 동일하다.)
<p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/09e4dfd2-e1f7-4118-8bb2-2adcdca236d0" width="500">
</p>
    
    
</details>
<!-------------------------------------------------------------------------------------------------------------------------------------------------------->
<details>
    <summary><b>Load Image 💬ED</b></summary>
<p></p>
<p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/6defb14b-7492-4a75-919a-f5632bc77ec5" width="300">
</p>
- 원래 Load Image에서 프롬프트 텍스트를 출력하게 수정한 노드이다.<p></p>
<li>큐를 돌리면 아래처럼 프롬프트, seed, 이미지 사이즈가 표시된다. <br>
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/5b18adb0-5e8e-4cc0-963d-287cb5d19e38" width="500"><br>
  (아쉽게도 이미 설치된 노드의 프롬프트만 추출할 수 있으며, 설치되지 않은 노드는 추출하지 못한다.)<br>
</li>
</details>
<!-------------------------------------------------------------------------------------------------------------------------------------------------------->
<details>
<p></p>
    <summary><b>Save Image 🔔ED</b></summary>
<p></p>
<p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/8e730793-1c61-4152-90a7-343de68d16a6" width="300">
</p>
- 원래 Save Image에서 Context입력을 추가하고 이미지를 입력 받으면 종소리가 들리게 수정한 노드.<p></p>
<li>Properties Panel에서 다음처럼 종소리 재생을 끄고 켜거나 음량을 조절할 수 있다. (음량 범위:0 ~ 1)<br>
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/946fcc7f-6a06-4377-bfde-4516d616bd55" width="500"><br>
</li>
<p></p>
<li>종소리를 바꾸고 싶으면 efficiency-nodes-comfyui\js\assets\notify.mp3 를 변경하면 된다.</li>
</details>
<!-------------------------------------------------------------------------------------------------------------------------------------------------------->
<details>
  <p></p>
  <summary><b>LoRA Stacker</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/857d98ec-b7f5-4957-9fc3-68a7245829cc" width="300">
  </p>
  - 최대 8개까지의 로라를 한번에 로딩할 수있는 노드이다.<p></p>
  <p></p>
  <li>Efficient Loader 💬ED와 마찬가지로 이름 입력 창은 하위 폴더별로 서브메뉴가 만들어지며 로라의 프리뷰 이미지 표시<br>
    <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/68240631-6962-4601-9f7a-2913a9eebedb" width="300"><br>
    <i>(로라의 프리뷰 이미지가 있다면 이름 옆에 '*'로 표시된다.</i><br>
    <i>폴더와 로라가 함께 있을땐 유형 별로 정렬이 안되는데 그땐 폴더 이름 맨 앞에 <code>-</code>를 붙여주면 정렬이 된다.)</i><br>
  </li>
  <p></p>
  <li>"🔍 View model info..."는 아래처럼 트리거 워드(Trained words)를 찾는데 편리하다.<br>
    <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/fe112563-4189-4d7e-aa41-72b8030fa69a" width="400">
  </li>
</details>
<!-------------------------------------------------------------------------------------------------------------------------------------------------------->
<details>
  <p></p>
  <summary><b>Embedding Stacker 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/66ca8ba4-f6e9-4881-ba8f-e737d8609515" width="400">
  </p>
  - 임베딩 일일이 치는거 스펠링도 기억안나고 짜증나서 하나 만들었다.<br>
  <i>(기능은 단순하게 💬ED 로더 positive, negative의 맨 마지막에 임베딩 문자열을 추가해준다.</i><br>
  <i> 💬ED 로더만 사용 가능함.)</i><br>
  <p></p>
  - 로라 스태커와 동일하게 "🔍 View model info..."로 정보를 볼 수 있다.<p></p>
</details>
<!-------------------------------------------------------------------------------------------------------------------------------------------------------->
<details>
  <p></p>
  <summary><b>Apply Lora Stack 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/f6e03a34-b05b-43fc-99be-2366610dd1ed" width="400">
  </p>
  - 로라 적용 시점을 늦추기 위해서 만든 노드이다. <br>
  <i>(💬ED 로더가 로라 스택을 로딩한 시점에서 로라가 적용되는데 FreeU나 IPAdapter등을 사용하면 로라를 적용한 모델을 변경하게 된다.</i><br>
  <i> {ex: 모델 로딩 -> 로라 적용 -> FreeU 또는 IPAdapter}</i><br>
  <i> 이것을 {모델 로딩 -> FreeU 또는 IPAdapter -> 로라 적용} 이렇게 순서를 바꾸게 하기 위해서 만든 노드이다.)</i><br>
  <p></p>
  <li>Context노드와 비슷하게 생겻듯이 동일한 기능을 한다. 단지 로라 스택 적용만 추가되었을 뿐이다.</li>
  <p></p>
  <li>Properties Panel에서 로라 적용을 켜고 끌 수 있으며, 로라 적용을 끄면 본래대로 💬ED 로더에서 로라 스택을 적용하고, Context노드와 완전히 같은 기능을 하게 된다.<br>
    <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/93cc64d6-9f85-47b9-ae59-a3faaeafb8ee" width="400">
  </li>
  <p></p>
  <li>로라 적용 순서를 바꾸면 이미지가 미묘하게 달라진다. 하지만 실제로 테스트하면 로라 적용을 미리 했을 때(Apply Lora Stack의 기능을 껐을 때) 더 퀄리티가 좋았다.</li>  
</details>
<!-------------------------------------------------------------------------------------------------------------------------------------------------------->
<details>
  <p></p>
  <summary><b>Control Net Script 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/4ebd0668-f182-40a0-a882-35fb485ede5c" width="400">
  </p>
  - 컨트롤넷 스크립트. 샘플러와 연결하여 컨트롤넷을 사용하는 노드.<br>
  <i>(KSampler (Efficient) 💬ED 또는 KSampler TEXT (Eff.) 💬ED에서만 동작한다.)</i><br>
</details>
<!-------------------------------------------------------------------------------------------------------------------------------------------------------->
<details>
  <p></p>
  <summary><b>FaceDetailer 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/3c79367f-e2f7-4f3c-bffe-48be9a6627c9" width="250">
  </p>
  - Impact pack의 FaceDetailer 애드온. Impact pack이 설치되지 않았다면 보이지 않는다.<p></p>
  - context를 입력받을 수 있게 수정한 버전.<p></p>
  - 💬ED 샘플러와 마찬가지로 set_seed_cfg_sampler 설정이 있으며, 각종 모델 로더를 통합한 노드.<p></p>
  <li>아래처럼 wildcard에 프롬프트 텍스트를 입력할 수 있다.<br>
    <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/9a8533a3-c1aa-4aac-b33a-f9c24636a790" width="400"><br>
    <i>(FaceDetailer 💬ED에서 눈을 더 반짝이게 하고 싶다던가 표정을 바꾸고 싶을 때 유용하다.</i><br>
    <i>프롬프트 텍스트를 입력하면 context의 프롬프트는 무시하고 입력된 프롬프트를 우선 사용한다.)</i><br>
  </li>
</details>
<details>
  <p></p>
  <summary><b>MaskDetailer 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/87bbd155-8b06-423d-b8e8-04a8f55b223d" width="250">
  </p>
  - Impact pack의 MaskDetailer 애드온. Impact pack이 설치되지 않았다면 보이지 않는다.<p></p>
  - context를 입력받을 수 있게 수정한 버전.<p></p>
  - 💬ED 샘플러와 마찬가지로 set_seed_cfg_sampler 설정이 있음.<p></p>
</details>
<details>
  <p></p>
  <summary><b>Detailer (SEGS) 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/c538b972-0e14-4b53-861d-ed0f78da0248" width="250">
  </p>
  - Impact pack의 Detailer (SEGS) 애드온. Impact pack이 설치되지 않았다면 보이지 않는다.<p></p>
  - context를 입력받을 수 있게 수정한 버전.<p></p>
  - 💬ED 샘플러와 마찬가지로 set_seed_cfg_sampler 설정이 있음.<p></p>
</details>
<details>
  <p></p>
  <summary><b>Ultimate SD Upscale 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/34fc20e4-8577-4716-9197-f63a31a6a31f" width="200">
  </p>
  - Ultimate SD Upscale의 애드온. Ultimate SD Upscale이 설치되지 않았다면 보이지 않는다.<p></p>
  - context를 입력받을 수 있게 수정한 버전.<p></p>
  - 💬ED 샘플러와 마찬가지로 set_seed_cfg_sampler 설정이 있으며, upscale 모델 로더를 통합한 노드.
</details>
<p></p>

### 요구사항:
<li>Efficiency Nodes 💬ED는 <a href="https://github.com/pythongosssss/ComfyUI-Custom-Scripts">ComfyUI-Custom-Scripts</a>가 필요함. <b>(필수)</b></li></li>
<p></p>
<li>FaceDetailer 💬ED 와 Ultimate SD Upscale 💬ED 사용을 위해서는 각각 <a href="https://github.com/ltdrdata/ComfyUI-Impact-Pack">Impact Pack</a>과 <a href="https://github.com/ssitu/ComfyUI_UltimateSDUpscale">Ultimate SD Upscale</a>이 필요함. <b>(선택)</b></li>
<p></p>
<li>context 입력, 출력 등을 위해 <a href="https://github.com/rgthree/rgthree-comfy">rgthree's custom nodes</a> 설치를 권장. <b>(선택)</b></li>
<p></p>

## **설치:**
매니저 -> Install via git URL -> https://github.com/NyaamZ/efficiency-nodes-comfyui 입력<br><br>

## ***에러 발생시 해결법***
대부분 뭐가 없으면 나오는 문제다. 그리고 아래 나오는 에러들은 커스텀 노드에서만 발생하는게 아니라 바닐라 CompyUI 에서도 똑같이 발생하는 에러다.<br><br>

<li>Load Image 에서 발생하는 에러 - 거기다 아무 이미지나 넣어주면 된다. (처음에 한번만 넣으면 됨.)</li><p></p>

<li>에피션트 로더 - 표시창에는 써져있지만 모델이나 VAE가 실제로 없을때 에러가 뜬다. 리프레시 누르고 모델을 설정해주면 해결.<br>
                         (모델은 반드시 있어야 한다. 없으면 매니저 > 인스톨 모델에서 checkpoints 검색해서 Type:checkpoints, Base: SD 1.5나 SDXL 을 다운.)</li><p></p>

<li>로라 스태커, 임베딩 스태커 - 표시창에는 써져있지만 로라나 임베딩이 실제로 없을때 에러가 뜬다. 리프레시 누르고 로라를 설정해주면 해결.</li><p></p>

<li>페이스 디테일러 - 표시창에는 써져있지만 모델이 없을때 에러가 뜬다. 리프레시 누르고 모델을 설정해주면 해결.<br>
                              (bbox_detector는 반드시 있어야 한다. 없으면 매니저 > 인스톨 모델 에서 bbox 검색해서 다운)</li><p></p>

<li>울티메이트 업스케일러 - 표시창에는 써져있지만 모델이 없을때 에러가 뜬다. 리프레시 누르고 모델을 설정해주면 해결.<br>
                                (업스케일 모델은 반드시 있어야 한다. 없으면 매니저 > 인스톨 모델 에서 upscale 검색해서 다운)</li><br><br>



## 알려진 버그
<li>----</li><p></p>
