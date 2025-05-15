**[[English]](https://github.com/NyaamZ/efficiency-nodes-ED/blob/main/README.md)**

✨🍬Efficiency Nodes에 기능을 추가하여 사용자 경험을 향상시키는 커스텀 노드. 오리지널 버전은 https://github.com/jags111/efficiency-nodes-comfyui 에서 확인.🍬

**Efficiency Nodes 💬ExtendeD (V8)**
=======



## 워크플로 예제:



###### 메인 워크플로

<div id="wrap">
    <div class="img-wrap"><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/workflows/workflow_Main.png" alt=""></div>
    <div class="txt-wrap"><p>(EXIF 있음)</p></div>
</div>



###### 리저널 워크플로

<div id="wrap">
    <div class="img-wrap"><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/workflows/workflow_regional.png" alt=""></div>
    <div class="txt-wrap"><p>(EXIF 있음)</p></div>
</div>




###### 플럭스 워크플로

<div id="wrap">
    <div class="img-wrap"><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/workflows/workflow_flux.png" alt=""></div>
    <div class="txt-wrap"><p>(EXIF 있음)</p></div>
</div>




## **기본 개요:**



- ## Context:

Efficiency Nodes 원본과 다르게 💬ED노드는 <code>context</code> 링크를 주고 받는다.

<code>context</code> 링크는 <code>model, clip, vae, conditioning</code> 등등 수많은 링크 등을 하나로 묶은 링크 다발이라고 생각하면 된다.

<p align="left">
  <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0001.jpg" width="600" style="display: inline-block;">
</p>

워크플로를 만들다 보면 위에 처럼 수많은 링크들로 스파게티처럼 만들어져 어질어질한데, 



<code>context</code> 링크를 사용하면 다음처럼 간단하게 만들 수 있다.

<p align="left">
  <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0002.png" width="600" style="display: inline-block;">
</p>


꼭 💬ED노드 사이에만 사용하는 것이 아니라 다른 노드에도 사용할 수 있음.

<div id="wrap">
    <div class="img-wrap"><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0003.png" alt=""></div>
    <div class="txt-wrap"><p>(EXIF 있음)</p></div>
</div>


Efficient Loader 💬ED에서 출력하는 <code>context</code> 링크는 다음이 포함되어 있다.

<div id="table">
    <table style="text-align: center;">
            <tbody>
                <tr>
                    <td rowspan="17" style="width:60%"><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0005.png" width="1200" style="display: inline-block;"></td>
                    <th style="background-color:palegreen;">context</th>
                    <td></td>
                </tr>
                <tr>
                    <th style="background-color:MediumPurple;">model</th>
                    <td></td>
                </tr>
                <tr>
                    <th style="background-color:Gold;">clip</th>
                    <td></td>
                </tr>
                <tr>
                    <th style="background-color:HotPink;">vae</th>
                    <td></td>
                </tr>
                <tr>
                    <th style="background-color:LightPink;">positive</th>
                    <td>conditioning</td>
                </tr>
                <tr>
                    <th style="background-color:LightPink;">negative</th>
                    <td>conditioning</td>
                </tr>
                <tr>
                    <th style="background-color:Plum;">latent</th>
                    <td></td>
                </tr>
                <tr>
                    <th style="background-color:LightSkyBlue;">image</th>
                    <td></td>
                </tr>
                <tr>
                    <th style="background-color:Gray;">seed</th>
                    <td></td>
                </tr>
                <tr>
                    <th style="background-color:Gray;">step_refiner</th>
                    <td>대신 batch_size가 들어있음</td>
                </tr>
                <tr>
                    <th style="background-color:Gray;">cfg</th>
                    <td></td>
                </tr>
                <tr>
                    <th style="background-color:Gray;">ckpt_name</th>
                    <td></td>
                </tr>
                <tr>
                    <th style="background-color:Gray;">clip_width</th>
                    <td>image width</td>
                </tr>
                <tr>
                    <th style="background-color:Gray;">clip_height</th>
                    <td>image height</td>
                </tr>
                <tr>
                    <th style="background-color:Gray;">text_pos_g</th>
                    <td>positive prompt</td>
                </tr>
                <tr>
                    <th style="background-color:Gray;">text_neg_g</th>
                    <td>negative prompt</td>
                </tr>
                <tr>
                    <th style="background-color:Gray;">mask</th>
                    <td></td>
                </tr>
            </tbody>
        </table>
</div>






- ## 체크 포인트, 로라, 인베딩 썸네일:

  Efficient Loader 💬ED, LoRA Stacker 💬ED, Embedding Stacker 💬ED 에서 모델을 선택할 때 썸네일이 표시된다.

   

  - 썸네일 스타일

    <p><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0006.png" alt="" width="600" style="display: inline-block;"></p>

  - 트리 스타일

    <p><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0007.png" alt="" width="600" style="display: inline-block;"></p>

  - settings > pysssss > combo++ > Lora/Checkpoint loader display mode 에서 스타일을 선택할 수 있음.

    <p align="left">
      <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0008.png" width="600" style="display: inline-block;">
    </p>

  - 썸네일은 처음에는 이미지가 없다고 보이지 않는데,
    Efficient Loader 💬ED나 LoRA Stacker 💬ED 등 에서 오른 클릭 > <code>🔍 View model info...</code>

     <p><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0017.png" width="500" style="display: inline-block;"></p>

    빨간 부분 - <code>Use as preview</code>를 눌러줘야 저장된다. (직접 모델 파일명.jpg 또는 png로 지정해줄 수 도 있음)

    




- ## 와일드 카드:

  Efficiency Nodes 💬ED는 와일드 카드를 지원함

   

  - ### 사용법

    - 와일드 카드는 Get booru Tag 💬ED의 `Select to add wildcard`를 눌러 쉽게 와일드 카드를 사용할 수 있음.

      <p align="left">
        <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0010.png" width="400" style="display: inline-block;">
      </p>

    - 와일드 카드 파일은 임팩트 팩의 와일드 카드를 공유함. `ComfyUI\custom_nodes\comfyui-impact-pack\wildcards`
    - 일반적인 와일드 카드 문법은 모두 사용가능. 하지만, 와일드 카드 안의 와일드 카드, 로라는 사용 불가.
    - 와일드 카드 인코딩은 Efficient Loader 💬ED에서 처리함. 때문에 와일드카드 사용시 반드시 Get booru Tag 💬ED를 쓸 필요는 없음
    - 주석 기능 #, //, /* */ 를 모두 지원함.

    

  - ### 순차적 와일드 카드

    - Get booru Tag 💬ED의 text_b 칸에 다음 처럼 \__와일드카드__#ASC0 이라고 적으면 된다.

      <p align="left">
        <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0010.png" width="400" style="display: inline-block;">
      </p>

    - #ASC숫자 는 와일드카드를 '숫자에서부터' 하나씩 올라가며 순회하고  (와일드 카드 최대 숫자에 도달하면 멈춤)

    - #DSC숫자 는 와일드카드를 '숫자에서부터' 하나씩 내려오며 순회한다. (0에 도달하면 멈춤)
      (와일드 카드의 갯수를 정확히 모를테니 #DSC1000 이렇게 대충 적으면 된다.)

    - #FIX숫자 는 고정.

    - 순차적 와일드 카드는 Get booru Tag 💬ED로만 가능.



- ## 리저널 프롬프트:

리저널 프롬프트는 영역별로 프롬프트를 달리하고 싶을 때 쓰는 방법이다. ([리저널 워크플로](https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/workflows/workflow_regional.png))

리저널 프롬프트 사용시 [**A8R8 ComfyUI Nodes**](https://github.com/ramyma/A8R8_ComfyUI_nodes) 노드 설치가 필요.

- ### 리저널 프롬프트 - Text 2 Image

  1. Regional Stacker 💬ED를 오른쪽 클릭, aspect ratio 에서 가로 세로 입력, <code>Create empty image</code>를 누른다. 누르면 자동으로 Efficient Loader 💬ED에 가로 세로가 입력되고, Regional Script 💬ED에 연결된 Load Image에 빈 이미지가 들어간다.

     <p align="left">
       <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0011.png" width="300" style="display: inline-block;">
     </p>

  1. 다음 처럼 마스크로 영역을 지정한 후, 프롬프트를 작성한다. (로라를 사용하고 싶으면 LoRA Stacker 💬ED를 붙이면 된다)

     <p align="left">
       <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0012.jpg" width="800" style="display: inline-block;">
     </p>

  1. 베이스 프롬프트에 다음처럼 적당한 프롬프트를 작성하고 큐 실행.

     <p align="left">
       <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0013.png" width="700" style="display: inline-block;">
     </p>

  1. 결과물

     <div id="wrap">
         <div class="img-wrap"><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0014.png" alt="" width="400" style="display: inline-block;"></div>
         <div class="txt-wrap"><p>(EXIF 있음)</p></div>
     </div>



- ### 리저널 프롬프트 - Image 2 Image

  1. [ComfyUI-ImageGallery-ED](https://github.com/NyaamZ/ComfyUI-ImageGallery-ED)가 설치 되어 있다면, 이미지를 더블클릭하면 다음처럼 이미지 갤러리가 열린다.

     <p align="left">
       <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0015.png" width="600" style="display: inline-block;">
     </p>

    2. 빨간 부분을 클릭하면 Regional Script 💬ED에 연결된 Load Image에 현재 이미지가 들어간다. 

    3. 마스크로 영역 지정, 프롬프트 작성후, 큐



- ## 컨트롤넷:

컨트롤 넷 사용은 다음처럼 Efficient Loader 💬ED에 Control Net Stacker를 붙여서 사용하면 된다.

<p align="left">
  <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0016.png" width="800" style="display: inline-block;">
</p>

컨트롤넷과 리저널 스크립트를 동시에 사용 가능.




- ## Get booru Tag:

   1. 단부루나 갤부루에서 괜찮은 이미지를 발견했다면, 이렇게 주소를 복사해서

      <p align="left">
        <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0018.jpg" width="600" style="display: inline-block;">
      </p>

   2. Get booru Tag 💬ED <code>url</code>에 넣어주면,

      <p><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0019.png" width="500" style="display: inline-block;"></p>

   3. 다음 처럼 실시간으로 태그를 추출해준다. (/* */는 주석임)

       <p><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0020.png" width="500" style="display: inline-block;"></p>




- ## Set_seed_cfg_sampler:

KSampler (Efficient) 💬ED, FaceDetailer 💬ED, Ultimate SD Upscale 💬ED 등에는 <code>set_seed_cfg_sampler</code> 위젯이 있다.
Efficient Loader 💬ED에서 seed, cfg, sampler, scheduler를 한 번만 설정하고 나머지는 일일이 설정하지 않아도 됨.

- <code>from context</code>는 Efficient Loader 💬ED에서 출력한 <code>context</code>에서 seed, cfg, sampler, scheduler 설정을 가져와서 사용.

- <code>from node to ctx</code>는 현재 노드의 seed, cfg, sampler, scheduler 설정을 <code>context</code>로 내보낸다.

- <code>from node only</code>는 현재 노드의 seed, cfg, sampler, scheduler 설정을 이용하고 <code>context</code>에 저장하지는 않음.

  

<p align="left">
  <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0023.png" width="400" style="display: inline-block;">
</p>







- ## XY 플롯:

AI로 그림을 뽑다보면 이런 생각이 들때가 있다. 더 그림을 선명하게 할 수는 없을까? 지금 cfg와 샘플러가 최적인걸까?

그럴 때 최적의 설정 값을 찾기 유용한 것이 xy플롯이다.

1. KSampler (Efficient) 💬ED 오른 클릭 > add script > XY plot

   <p align="left">
     <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0024.png" width="500" style="display: inline-block;">
   </p>

2. XY plot 오른 클릭 > Add X input > XY Input: Sampler/Scheduler
   XY plot 오른 클릭 > Add Y input > XY Input: Sampler/Scheduler

   <p><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0025.png" width="500" style="display: inline-block;"></p>

3. 큐를 돌리면 다음처럼 한눈에 적절한 설정 값을 확인할 수 있다.

    <p><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0026.jpg" width="700" style="display: inline-block;"></p>





- ## Refiner script:

리파이너 스크립트는 KSampler (Advanced)를 차용한 노드이다.

- ### 용도

     1. Hires FIx
     1. 다른 모델로 리파이닝하기 (색감, 텍스쳐 같은걸 변경시킬 수 있다.)

 Ultimate SD Upscale 💬ED로 Hires FIx하면 느리기도 하거니와 배꼽이 두 개가 되는 것 처럼 이미지가 변형될 경우가 있다. 
  그럴때 Refiner script로 Hires FIx하면 훨씬 낫다.

- ### Refiner script로 Hires FIx 하는법

   1. Load Image 💬ED의 <code>upscale_method</code>와 <code>keep_proportions</code>를 이용해 2배로 업스케일. 
      (<code>keep_proportions</code>를 2x로 설정하면 <code>width, height</code>를 일일히 입력하지 않아도 자동으로 맞춰준다.)
   
      <p align="left">
        <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0035.png" width="400" style="display: inline-block;">
      </p>
   
     2. KSampler (Efficient) 💬ED 오른클릭 > Add script > Refiner Script 💬ED 추가
        <code>steps, denoise, start_at_step</code>을 설정한다. 
        (Hires FIx 할 때 <code>start_at_step</code>은 <code>step</code>의 절반 정도가 적당한 듯. 직접 최적의 <code>denoise, start_at_step</code> 값을 찾아보자)
   
        <p align="left">
          <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0036.png" width="600" style="display: inline-block;">
        </p>
   
   3. 큐를 돌린다.
   
      <div id="wrap">
          <div class="img-wrap"><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0037.png" alt="" width="400" style="display: inline-block;"></div>
          <div class="txt-wrap"><p>(EXIF 있음)</p></div>
      </div>




## 💬ED 노드 설명:
<details>
    <summary><b>Efficient Loader 💬ED</b></summary>
<ul>
        <p></p>
    <li>대략 Load Checkpoint, CLIP Set Last Layer, Empty Latent Image, Repeat Latent Batch 등을 하나로 묶은 것.<br><i>(단순히 네 가지를 합친 것보다 훨씬 더 다양한 기능)</i><br>
      <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0021.png" width="250" style="display: inline-block;">
      </li>
    <p></p>
    <li>위의 노드 묶음과 달리 클릭 한번으로 <code>Txt2Img</code>, <code>Img2Img</code>, <code>Inpaint</code> 모드 설정이 가능하다.<br><i>(<code>Txt2Img</code>로 설정시 연결된 Ksampler (Efficient) 💬ED의 <code>denoise</code> 값이 자동으로 1로 설정됨.)</i><br>
      <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/0f8549b8-cbe0-4662-b922-df21545e2d8f" width="250" style="display: inline-block;">
      </li>
    <p></p>
    <li><code>Inpaint(MaskDetailer)</code> 모드 추가.<br><i>(그냥 Inpaint를 사용하면 점점 화질이 열화되는데 Impact Pack의 MaskDetailer를 차용해 보다 나은 이미지 품질이 가능함.</i><br>
      <i>자세한 것은 <code>Inpaint(MaskDetailer)</code>에서 설명.)</i><br>
      <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/5b04b764-f995-4350-b897-e42041686a2d" width="250" style="display: inline-block;">
      </li>
    <li>seed, cfg, sampler, scheduler를 설정하고 <code>context</code>에 저장. 후에 Ksampler (Efficient) 💬ED등에서 그 설정값을 이용할 수 있다.</li>
    <p></p>
    <li>오른 클릭의 드롭다운 메뉴<br>
        <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/47995eca-94fb-4e52-b77b-2a53e9f292d0" width="150" style="display: inline-block;">
        <p> <code>🔍 View model info...</code>는 모델의 정보를 표시한다.<br>          
          <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/f7cf378c-cd8a-49cb-9389-5681caacf130" width="250" style="display: inline-block;"><br>
          <i>(<code>🔍 View model info...</code>는 크기가 큰 모델은 해쉬값을 찾느라 '첫' 로딩이 느리다. 처음 한번은 "<code>Use as preview</code>"를 눌러 주는걸 권장.)</i><br></p>
        <p> <code>📐 Aspect Ratio...</code>는 <code>image_width</code>와 <code>image_height</code>에 선택한 값을 입력한다.<br>
          <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/f92fdd33-ddcb-4b42-904c-4c67a52e4aa0" width="250" style="display: inline-block;"><br>
          <i>(<code>Txt2Img</code> 모드로 이미지를 만들 때 편리하다. ◆ 표시는 추천 해상도)</i><br></p>
    </li>
    <p></p>
    <li>Tiled VAE 인코딩<br>
        <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/b160f24f-09f6-460f-a1a4-e906077ff61b" width="300" style="display: inline-block;"><br>
          - 오른 클릭 > Property Panel에서 <code>Use tiled VAE encode</code>를 true로 하면 VAE 인코딩시에 Tiled VAE 인코딩을 사용한다.<br>
          - Tiled VAE 인코딩은 큰 이미지를 VRAM이 부족해도 인코딩할 수 있다. 대신 기본보다 느리다.<br>
    </li>
    <p></p>
    <li>로라, 임베딩, 컨트롤 넷 스태커를 <code>lora_stack</code>과 <code>cnet_stack</code>에 연결 가능.</li>
    <p></p>
    <li>Property Panel에서 <code>Token normalization</code>과 <code>Weight interpretation</code>으로 프롬프트 <a href="https://github.com/BlenderNeko/ComfyUI_ADV_CLIP_emb">인코딩</a> 방식 설정 가능.</li>
    <p></p>
    <li>Property Panel에서 <code>Use Latent Rebatch</code>로 배치 타입 설정 가능. true(기본값)로 설정하면 배치를 한 번에 처리하는 것이 아니라 나눠서 처리한다.</li>
    <p></p>
    <li><code>Clip skip</code>은 0으로 설정하면 <code>Clip skip</code>을 건너뜀.</li>
    <p></p>
</ul>
</details>



<details>
    <summary><b>KSampler (Efficient) 💬ED</b></summary>
<p></p>
- 원래 에피션트 노드에 <code>context</code>를 입력 받을 수 있게 수정한 노드.<p></p>
- 이미지를 샘플링 후 이미지를 <code>CONTEXT</code>와 <code>OUTPUT_IMAGE</code>에 출력, <code>steps</code>는 <code>STEPS_INT</code>에 출력한다.<p></p>
<p align="left">
  <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0022.png" width="500">
</p>
    <p></p>   
    <p></p>
    <li>VAE decode 설정<br>
      - Properties Panel에서 <code>Use tiled VAE decode</code>를 true로 하면 된다.<br>
    </li>
</details>


<details>
    <summary><b>Inpaint(MaskDetailer) 모드</b></summary>
<p></p>
- Efficient Loader 💬ED에서 Inpaint(MaskDetailer) 모드를 선택하면 에피션트 샘플러 💬ED가 마스크 디테일러 모드로 변경된다.<p></p>
- Impact Pack의 MaskDetailer를 그대로 통합시킴.<p></p>
- 인페인트하면서 화질의 열화가 일어나지 않는다. 이미지 퀄리티가 더 낫다.<br>
  (사용법은 기존의 MaskDetailer와 동일하다. 디테일러의 사용법은 <a href="https://arca.live/b/aiart/126870050">여기를</a> 참조)
<p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/09e4dfd2-e1f7-4118-8bb2-2adcdca236d0" width="400">
</p>
- 마스크 디테일러의 <code>drop size, cycle, inpaint model, noise mask feather</code>는 Property Panel에서 설정 할 수 있음<p></p>
</details>



<details>
    <summary><b>Load Image 💬ED</b></summary>
<p></p>
<p align="left">
  <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0026.png" width="400">
</p>
- 이미지 로딩과 업스케일을 합친 노드. 프롬프트 텍스트도 출력된다.<p></p>
<li>이미지 업스케일은 <code>upscale_method</code>에서 업스케일 방식을 선택, <code>width</code>와 <code>height</code>를 입력하면 된다.<br>
  <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0027.png" width="400"><br>
</li>
<li><code>keep_proportions</code>으로 이미지의 비율을 유지한 채 업스케일을 할 수 있다.</li>
<li>1.5x, 2x, 3x등은 <code>width, height</code>의 값을 무시하며 비율에 맞게 가로, 세로를 자동으로 조절한다.</li>
<li><code>based on width</code>는 <code>width</code>에 입력받은 크기를 유지한 채로 비율에 맞게 세로를 자동으로 조절한다.</li>
<p></p>
- 큐를 돌리면 아래처럼 프롬프트, seed가 표시된다. <br>
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/5b18adb0-5e8e-4cc0-963d-287cb5d19e38" width="700"><br>
  (설치된 노드의 프롬프트만 추출할 수 있으며, 설치되지 않은 노드는 추출하지 못한다.)<br>
</details>


<details>
<p></p>
    <summary><b>Save Image 🔔ED</b></summary>
<p></p>
<p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/8e730793-1c61-4152-90a7-343de68d16a6" width="300">
</p>
- Save Image에 <code>context</code>입력을 추가하고 이미지를 입력 받으면 종소리가 들리게 수정한 노드.<p></p>
<li>Properties Panel에서 <code>Play sound, Sound Volume</code>으로 종소리를 끄고 켜거나 음량을 조절할 수 있다. (음량 범위:0 ~ 1)<br>
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/946fcc7f-6a06-4377-bfde-4516d616bd55" width="500"><br>
</li>
<p></p>
<li>종소리를 바꾸고 싶으면 <code>efficiency-nodes-comfyui\js\assets\notify.mp3</code> 를 변경하면 된다.</li>
</details>


<details>
  <p></p>
  <summary><b>LoRA Stacker 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/user-attachments/assets/a8b132f3-65d5-4bc9-a44d-566b1e9a4b33" width="300">
  </p>
  - 최대 9개까지의 로라를 한번에 로딩할 수있는 노드이다.<p></p>
  <p></p>
  <li>Efficient Loader 💬ED와 마찬가지로 이름 입력 창은 하위 폴더별로 서브메뉴가 만들어지며 로라의 프리뷰 이미지 표시<br>
    <img src="https://github.com/user-attachments/assets/2e98c870-1d8f-407d-83da-953c6ab13e87" width="300"><br>
    <i>폴더와 로라가 함께 있을땐 유형 별로 정렬이 안되는데 그땐 폴더 이름 맨 앞에 <code>-</code>를 붙여주면 정렬이 된다.)</i><br>
  </li>
  <p></p>
  <li><code>🔍 View model info...</code>는 아래처럼 트리거 워드(Trained words)를 찾는데 편리하다.<br>
    <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/fe112563-4189-4d7e-aa41-72b8030fa69a" width="400">
  </li>
</details>


<details>
  <p></p>
  <summary><b>Embedding Stacker 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/66ca8ba4-f6e9-4881-ba8f-e737d8609515" width="400">
  </p>
  - 임베딩 일일이 치는거 스펠링도 기억안나고 짜증나서 하나 만들었다.<br>
  <i>(기능은 단순하게 Efficient Loader 💬ED의 positive, negative 프롬프트 마지막에 임베딩 문자열을 추가해준다.</i><br>
  <i> Efficient Loader 💬ED만 작동함.)</i><br>
  <p></p>
  - 로라 스태커와 동일하게 <code>🔍 View model info...</code>로 정보를 볼 수 있다.<p></p>
</details>


<details>
  <p></p>
  <summary><b>Wildcard Encode 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0028.png" width="400">
  </p>
  - Efficient Loader 💬ED의 <code>Use Latent Rebatch</code>가 true일때 와일드 카드를 처리하는 노드.<br>
  <i>(배치 별로 와일드 카드를 따로 적용하게 하기 위해서 만들었음)</i><br>
  <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0029.png" width="600">
  <p></p>
  <li>Context노드와 비슷하게 생겻듯이 동일한 기능을 함.</li>
  <p></p>
  <li>Properties Panel에서 <code>Turn on Apply Lora</code>를 true로 하면, 로라 적용을 시점을 늦출 수 있음.<br>
    <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0030.png" width="400">
  </li>
  <p></p>
</details>


<details>
  <p></p>
  <summary><b>TIPO Script 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0032.png" width="250">
  </p>
  - TIPO노드에 <code>context</code>를 입력받을 수 있게 수정한 버전.<p></p>
  - 프롬프트를 랜덤하게 뽑아주는 노드이다. 자세한 것은 <a href="https://github.com/KohakuBlueleaf/z-tipo-extension">여기를</a> 참조<p></p>
  - 사용을 위해선 z-tipo-extension 설치가 필요하다.<p></p>
</details>


<details>
  <p></p>
  <summary><b>Regional Stacker 💬ED, Regional Script 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0038.png" width="500">
  </p>
  - 리저널 프롬프트에 사용하는 노드.<p></p>
  - Regional Script 💬ED의 <code>url</code>은 Get booru Tag 💬ED <code>url</code>과 같다. 갤부루나 단부루의 태그를 가져올 수 있다.<p></p>
  - Regional Script 💬ED의 프롬프트 창은 와일드 카드 입력 가능.<p></p>
</details>



<details>
  <p></p>
  <summary><b>Refiner Script 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="D:\ComfyUI_windows_portable\ComfyUI\custom_nodes\efficiency-nodes-ED\html_resource\0039.png" width="300">
  </p>
  - KSampler (Efficient) 💬ED노드에 리파이닝 작업을 추가해주는 노드.<p></p>
  - Load Checkpoint를 붙여 다음처럼 다른 모델로 리파이닝 할 수 있다.<br><img src="D:\ComfyUI_windows_portable\ComfyUI\custom_nodes\efficiency-nodes-ED\html_resource\0040.png" width="500"><p></p>
  - <code>ignore_batch_size</code> true는 배치 사이즈를 무시하고 한 번만 작업.<p></p>
  - <code>do_refine_only</code> true는 리파이닝만. false는 이미지를 샘플링 한후 리파이닝.<p></p>
</details>



<details>
  <p></p>
  <summary><b>Int Holder 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0033.png" width="400">
  </p>
  - KSampler (Efficient) 💬ED로 이미지를 만들면 <code>steps</code>을 기억하고 있다가 Hires Fix 실행 시에 <code>context</code>에 저장하는 노드, <p></p>
  - FaceDetailer 💬ED, Ultimate SD Upscale 💬ED는 <code>context</code>에 <code>steps</code>가 들어 있다면 그걸 우선 꺼내서 사용함.<p></p>
  - <code>steps</code>를 일일이 다시 입력하기 귀찮아서 만든 노드.<p></p>
</details>


<details>
  <p></p>
  <summary><b>FaceDetailer 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/3c79367f-e2f7-4f3c-bffe-48be9a6627c9" width="250">
  </p>
  - Impact pack의 FaceDetailer 애드온.<p></p>
  - <code>context</code>를 입력받을 수 있게 수정한 버전.<p></p>
  - KSampler (Efficient) 💬ED와 마찬가지로 <code>set_seed_cfg_sampler</code> 설정이 있으며, 각종 모델 로더를 통합한 노드.<p></p>
  - 디테일러의 사용법은 <a href="https://arca.live/b/aiart/126870050">여기를</a> 참조<p></p>
  <li>아래처럼 <code>wildcard</code>에 프롬프트 텍스트를 입력할 수 있다.<br>
    <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0031.png" width="400"><br>
    <i>(FaceDetailer 💬ED에서 눈을 더 반짝이게 하고 싶다던가 표정을 바꾸고 싶을 때 유용하다.</i><br>
    <i>디테일러 프롬프트에 대한 것은 <a href="https://arca.live/b/aiart/126917339">여기를</a> 참조)</i><br>
  </li>
</details>


<details>
  <p></p>
  <summary><b>MaskDetailer 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/87bbd155-8b06-423d-b8e8-04a8f55b223d" width="250">
  </p>
  - Impact pack의 MaskDetailer 애드온.<p></p>
  - <code>context</code>를 입력받을 수 있게 수정한 버전.<p></p>
  - KSampler (Efficient) 💬ED와 마찬가지로 <code>set_seed_cfg_sampler</code> 설정이 있음.<p></p>
</details>


<details>
  <p></p>
  <summary><b>Detailer (SEGS) 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/c538b972-0e14-4b53-861d-ed0f78da0248" width="250">
  </p>
  - Impact pack의 Detailer (SEGS) 애드온.<p></p>
  - <code>context</code>를 입력받을 수 있게 수정한 버전.<p></p>
  - KSampler (Efficient) 💬ED와 마찬가지로 <code>set_seed_cfg_sampler</code> 설정이 있음.<p></p>
</details>


<details>
  <p></p>
  <summary><b>Ultimate SD Upscale 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/34fc20e4-8577-4716-9197-f63a31a6a31f" width="200">
  </p>
  - Ultimate SD Upscale의 애드온.<p></p>
  - <code>context</code>를 입력받을 수 있게 수정한 버전.<p></p>
  - KSampler (Efficient) 💬ED와 마찬가지로 <code>set_seed_cfg_sampler</code> 설정이 있으며, upscale 모델 로더를 통합한 노드.
</details>


<details>
  <p></p>
  <summary><b>SUPIR 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/user-attachments/assets/ef20c2cf-e0fa-4505-a432-50a97d0cb7f4" width="400">
  </p>
  - ComfyUI-SUPIR의 애드온. SUPIR는 High-res Fix에 탁월한 성능을 보여주지만 6개나 되는 노드가 필요한데, 그것을 단 두 개로 줄였다.<p></p>
  - SUPIR는 전용 모델이 필요하다. 모델 다운 및 자세한 것은 <a href="https://github.com/kijai/ComfyUI-SUPIR">여기를</a> 참조<p></p>
  - KSampler (Efficient) 💬ED와 마찬가지로 <code>set_seed_cfg_sampler</code> 설정이 있으며, 로더는 upscale + SUPIR 모델 로더와 업스케일러가 통합되어 있음.<p></p>
  - 업스케일은 업스케일 모델로 업스케일 하고 나서 원하는 크기에 맞춰 다운 스케일하고 upscaled image에 출력한다.<p></p>
  - <a href="https://github.com/kijai/ComfyUI-SUPIR">ComfyUI-SUPIR</a>  설치 필요.<p></p>
  - 예시 동영상<p></p>
<video  src="https://github.com/kijai/ComfyUI-SUPIR/assets/40791699/5cae2a24-d425-462c-b89d-df7dcf01595c"  controls>예시 동영상  </video> 
</details>
<p></p>

<p></p>

## **설치:**
1. 매니저 > 커스텀 노드 매니저 > 검색에서 다음을 설치

   [**ComfyUI Impact Pack**](https://github.com/ltdrdata/ComfyUI-Impact-Pack)

   [**ComfyUI Impact Subpack**](https://github.com/ltdrdata/ComfyUI-Impact-Subpack)

   [**ComfyUI-Custom-Scripts**](https://github.com/pythongosssss/ComfyUI-Custom-Scripts)  (필수!)

   [**ComfyUI_UltimateSDUpscale**](https://github.com/ssitu/ComfyUI_UltimateSDUpscale)

   [**rgthree-comfy**](https://github.com/rgthree/rgthree-comfy)

   [**efficiency-nodes-comfyui**](https://github.com/jags111/efficiency-nodes-comfyui)  (필수!)

   [**efficiency-nodes-ED**](https://github.com/NyaamZ/efficiency-nodes-ED)  (본체)

   [**ComfyUI-ImageGallery-ED**](https://github.com/NyaamZ/ComfyUI-ImageGallery-ED)  (같이 써야 편리)

   [**ComfyUI_BiRefNet_ll**](https://github.com/lldacing/ComfyUI_BiRefNet_ll)  (선택)

   [**z-tipo-extension**](https://github.com/KohakuBlueleaf/z-tipo-extension)  (선택)

   [**A8R8 ComfyUI Nodes**](https://github.com/ramyma/A8R8_ComfyUI_nodes)  (선택)


2. 설치 후 > 리스타트 > Update All > 리스타트 >
   ComfyUI\custom_nodes\efficiency-nodes-ED\start.bat 실행



## ***에러 발생시 해결법***
대부분 뭐가 없으면 나오는 문제. 그리고 아래 나오는 에러들은 커스텀 노드에서만 발생하는게 아니라,바닐라 ComfyUI 에서도 똑같이 발생하는 에러임.

- Load Image 💬ED 에서 발생하는 에러 - 거기다 아무 이미지나 넣어주면 된다. (처음에 한번만 넣으면 됨.)
- Efficient Loader 💬ED - 표시창에는 써져있지만 모델이나 VAE가 실제로 없을 때 에러가 뜬다. 
- LoRA Stacker 💬ED - 표시창에는 써져있지만 로라나 임베딩이 실제로 없을 때 에러. 리프레시 누르고 로라를 설정해주면 해결.
- FaceDetailer 💬ED - 표시창에는 써져있지만 모델이 없을때 에러가 뜬다. 모델을 다운, 리프레시 누르고 설정해주면 해결.
- Ultimate SD Upscale 💬ED - 표시창에는 써져있지만 모델이 없을 때 에러가 뜬다. 모델을 다운, 리프레시 누르고 설정해주면 해결.
  (bbox, sam, upscaler 모델 다운은 매니저 > 모델 메니저 >검색 창에 검색)



- FaceDetailer 💬ED, Ultimate SD Upscale 💬ED의 steps가 멋대로 고정되는 문제는 이 노드(Int Holder 💬ED) 때문임.

    <p><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0034.png" width="250" style="display: inline-block;"></p>

​        KSampler (Efficient) 💬ED로 이미지를 만들면 steps을 기억하고 있다가 Hires Fix 실행 시에 <code>context</code>에 저장하는 노드인데,

​        (FaceDetailer 💬ED, Ultimate SD Upscale 💬ED는 <code>context</code>에 steps가 들어 있다면 그걸 우선 꺼내서 사용함. 
​           steps를 일일이 다시 입력하기 귀찮아서 만든 노드),

​        불필요하거나 직접 steps를 입력하려면, 이 노드를 바이패스하거나 또는 삭제하고,
​        Ctx 노드의 steps와 KsamplerED의 steps_int의 연결을 끊으면 됨.



## 알려진 버그

- <code>🔍 View model info...</code>를 했을 때 [civitai.com](https://unsafelink.com/https://civitai.com/) 에서 다음처럼 모델을 못찾는 버그가 있음.
   
   <p><img src="D:\ComfyUI_windows_portable\ComfyUI\custom_nodes\efficiency-nodes-ED\html_resource\0041.png" width="400" style="display: inline-block;"></p>
   
    해시 값이 안맞아서 발생하는 문제인데
   
   <p><img src="D:\ComfyUI_windows_portable\ComfyUI\custom_nodes\efficiency-nodes-ED\html_resource\0042.jpg" width="800" style="display: inline-block;"></p>
   
   [civitai.com](https://unsafelink.com/https://civitai.com/) 에서 빨갛게 칠해진 부분을 클릭해서 해시 값을 복사한 다음.
   
   <code>ComfyUI\models\checkpoints\모델명.sha256</code> 을 메모장으로 열어서 복사한 값을 덮어쓰면 됨.

