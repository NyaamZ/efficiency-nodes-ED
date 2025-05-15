**[[한국어]](https://github.com/NyaamZ/efficiency-nodes-ED/blob/main/README_KR.md)**

✨🍬A version of Efficiency Nodes for ComfyUI that improves UX by adding various features. See https://github.com/jags111/efficiency-nodes-comfyui for the original description.🍬


<b>Efficiency Nodes 💬ExtendeD (V8)</b>
=======

### Example workflow:
<p align="left">
  <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/workflows/workflow_regional.png" width="800" style="display: inline-block;">
</p>
Unlike the original, 💬ED nodes send and receive Context links.<br>



### Added 💬ED nodes:
<!-------------------------------------------------------------------------------------------------------------------------------------------------------->
<details>
    <summary><b>Efficient Loader 💬ED</b></summary>
<ul>
    <p></p>
    <li>Txt2Img, Img2Img, and Inpaint modes can be set with a single click.<br><i>(When set to Txt2Img, the denoise value of the associated Ksampler (Efficient) 💬ED is automatically set to 1.)</i><br>
      <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/0f8549b8-cbe0-4662-b922-df21545e2d8f" width="250" style="display: inline-block;">
      </li>
    <p></p>
    <li>Added Inpaint (MaskDetailer) mode.<br>
      <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/5b04b764-f995-4350-b897-e42041686a2d" width="250" style="display: inline-block;">
      </li>
    <li>Set seed, cfg, sampler, scheduler and save them in context. Later, you can use those settings in Ksampler (Efficient) 💬ED, etc.</li>
    <p></p>
    <li>Add a drop-down menu on right-click.<br>
        <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/47995eca-94fb-4e52-b77b-2a53e9f292d0" width="150" style="display: inline-block;">
        <p> "🔍 View model info...”displays the model's information.<br>          
          <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/f7cf378c-cd8a-49cb-9389-5681caacf130" width="250" style="display: inline-block;"><br>
          <br></p>
        <p> "📐 Aspect Ratio...”enters the selected values for image_width and image_height.<br>
          <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/f92fdd33-ddcb-4b42-904c-4c67a52e4aa0" width="250" style="display: inline-block;"><br>
          <i>(Convenient when creating images in Txt2Img mode. ◆ Marked is the recommended resolution)</i><br></p>
    </li>
    <li>Showing preview images when selecting a model<br>
        <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/9ff41533-ba10-4707-a61b-61167aea23a9" width="250" style="display: inline-block;"><br>
    </li>
    <p></p>
    <li>Tiled VAE Encoding<br>
        <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/b160f24f-09f6-460f-a1a4-e906077ff61b" width="300" style="display: inline-block;"><br>
          - In the Right-click > Property Panel, set 'Use tiled VAE encode' to true to use tiled VAE encoding for VAE encoding.<br>
    </li>
    <p></p>
</ul>
</details>
<!-------------------------------------------------------------------------------------------------------------------------------------------------------->
<details>
    <summary><b>KSampler (Efficient) 💬ED</b></summary>
<p></p>
- Modified to accept context input from the original efficency node.<p></p>

<p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/37ca01cb-0b8e-4e14-9d86-7dcf09c3a481" width="500">
</p>
    <p></p>
    <li>Setting set_seed_cfg_sampler to import or export seed, cfg, sampler, and scheduler settings from context<br>
      <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/57694db3-b520-47ef-b401-8fcbfd1eb63b" width="250" style="display: inline-block;"><br>
      - 'from node to ctx' exports the current node's seed, cfg, sampler, scheduler settings to context.<br>
      - 'from context' gets seed, cfg, sampler, scheduler settings from context.<br>
      - 'from node only' uses the current node's seed, cfg, sampler, and scheduler settings and does not store them in context.<br>
    </li>    
    <p></p>
    <li>VAE decode settings<br
      - After sampling, you can choose what to use when VAE decoding for image generation.<br>
      - In the Properties Panel, set 'Use tiled VAE decode' to true.<br>
    </li>
</details>
<!-------------------------------------------------------------------------------------------------------------------------------------------------------->
<details>
    <summary><b>Inpaint(MaskDetailer) mode</b></summary>
<p></p>
- When you select Inpaint(MaskDetailer) mode in Efficient Loader 💬ED, Efficient Sampler 💬ED changes to Mask Detailer mode.<p></p>
- MaskDetailer from the Impact Pack has been integrated into the sampler. (The usage is the same as the existing MaskDetailer.)<p></p>
<p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/09e4dfd2-e1f7-4118-8bb2-2adcdca236d0" width="500">
</p>

​    
</details>
<!-------------------------------------------------------------------------------------------------------------------------------------------------------->
<details>
    <summary><b>Load Image 💬ED</b></summary>
<p></p>
<p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/6defb14b-7492-4a75-919a-f5632bc77ec5" width="300">
</p>
- This is the node that added the prompt text output from the original 'Load Image'.<p></p>
<li><img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/5b18adb0-5e8e-4cc0-963d-287cb5d19e38" width="500"><br></li>
</details>
<!-------------------------------------------------------------------------------------------------------------------------------------------------------->
<details>
<p></p>
    <summary><b>Save Image 🔔ED</b></summary>
<p></p>
<p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/8e730793-1c61-4152-90a7-343de68d16a6" width="300">
</p>
- A node modified from the original 'Save Image' to play a bell when an image is input.<p></p>
<li>You can adjust the volume in the Properties Panel.<br>
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/946fcc7f-6a06-4377-bfde-4516d616bd55" width="500"><br>
</li>
<p></p>
<li>If you want to change the bell sound, you can change efficiency-nodes-ED\js\assets\notify.mp3</li>
</details>
<!-------------------------------------------------------------------------------------------------------------------------------------------------------->
<details>
  <p></p>
  <summary><b>LoRA Stacker💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/user-attachments/assets/a8b132f3-65d5-4bc9-a44d-566b1e9a4b33" width="300">
  </p>
  <p></p>
  <li>As with Efficient Loader 💬ED, you'll see a preview image of Lora.<br>
    <img src="https://github.com/user-attachments/assets/2e98c870-1d8f-407d-83da-953c6ab13e87" width="300"><br>    
  </li>
  <p></p>
</details>
<!-------------------------------------------------------------------------------------------------------------------------------------------------------->
<details>
  <p></p>
  <summary><b>Embedding Stacker 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/66ca8ba4-f6e9-4881-ba8f-e737d8609515" width="400">
  </p>
  - This is a simple function that adds embedding to the end of positive and negative strings in the 💬ED loader.<br>
  <i>Works with 💬ED loader only.</i><br>
  <p></p>
</details>
<!-------------------------------------------------------------------------------------------------------------------------------------------------------->
<details>
  <p></p>
  <summary><b>Apply Lora Stack 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/f6e03a34-b05b-43fc-99be-2366610dd1ed" width="400">
  </p>
  - This node is created to delay the point at which Lora is applied.<br>
  <li>It looks similar to the Context node and does the same thing. It just adds apply of the Lora stack.</li>
  <p></p>
  <li>You can toggle Lora application in the Properties Panel, and if you disable Lora apply, it will behave exactly like a Context node.<br>
    <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/93cc64d6-9f85-47b9-ae59-a3faaeafb8ee" width="400">
  </li>
</details>
<!-------------------------------------------------------------------------------------------------------------------------------------------------------->
<details>
  <p></p>
  <summary><b>Control Net Script 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/4ebd0668-f182-40a0-a882-35fb485ede5c" width="400">
  </p>
  - ControlNet scripts. A node that uses ControlNet in connection with a sampler.<br>
  <i>Only works with KSampler (Efficient) 💬ED.</i><br>
</details>
<!-------------------------------------------------------------------------------------------------------------------------------------------------------->
<details>
  <p></p>
  <summary><b>FaceDetailer 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/3c79367f-e2f7-4f3c-bffe-48be9a6627c9" width="250">
  </p>
  - FaceDetailer add-on from the Impact pack. Not visible if the Impact pack is not installed.<p></p>
  - Node modified to accept context input.<p></p>
  - Like the '💬ED sampler', there is a set_seed_cfg_sampler setting.<p></p>
</details>
<details>
  <p></p>
  <summary><b>MaskDetailer 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/87bbd155-8b06-423d-b8e8-04a8f55b223d" width="250">
  </p>
  - MaskDetailer add-on from the Impact pack. Not visible if the Impact pack is not installed.<p></p>
  - Node modified to accept context input.<p></p>
  - Like the '💬ED sampler', there is a set_seed_cfg_sampler setting.<p></p>
</details>
<details>
  <p></p>
  <summary><b>Detailer (SEGS) 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/c538b972-0e14-4b53-861d-ed0f78da0248" width="250">
  </p>
  - Detailer (SEGS) add-on from the Impact pack. Not visible if the Impact pack is not installed.<p></p>
  - Node modified to accept context input.<p></p>
  - Like the '💬ED sampler', there is a set_seed_cfg_sampler setting.<p></p>
</details>
<details>
  <p></p>
  <summary><b>Ultimate SD Upscale 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/34fc20e4-8577-4716-9197-f63a31a6a31f" width="200">
  </p>
  - Ultimate SD Upscale add-on from the Impact pack. Not visible if the Ultimate SD Upscale is not installed.<p></p>
  - Node modified to accept context input.<p></p>
  - Like the '💬ED sampler', there is a set_seed_cfg_sampler setting.<p></p>
</details>
<details>
  <p></p>
  <summary><b>SUPIR 💬ED</b></summary>
  <p></p>
  <p align="left">
  <img src="https://github.com/user-attachments/assets/ef20c2cf-e0fa-4505-a432-50a97d0cb7f4" width="400">
  </p>
  - ComfyUI-SUPIR add-on. SUPIR is great for high-res fixes, but it requires six nodes, which I reduced to just two.<p></p>
  - Like the 💬ED sampler, there is a 'set_seed_cfg_sampler' setting, and the loader is a combination of upscale model + SUPIR loader and upscaler.<p></p>
  - Upscale using the model, then downscale to 'upscale by' and output to the upscaled image.
</details>
<p></p>

### Requirements:
<li><a href="https://github.com/jags111/efficiency-nodes-comfyui">Efficiency Nodes for ComfyUI</a> is <b>MUST</b> required.</li>
<li><a href="https://github.com/pythongosssss/ComfyUI-Custom-Scripts">ComfyUI-Custom-Scripts</a> is <b>MUST</b> required.</li>
<p></p>
<li>FaceDetailer 💬ED addon requires <a href="https://github.com/ltdrdata/ComfyUI-Impact-Pack">Impact Pack</a></li>
<li>Ultimate SD 💬ED addon requires <a href="https://github.com/ssitu/ComfyUI_UltimateSDUpscale">Ultimate SD Upscale</a></li>
<li>SUPIR 💬ED addon requires <a href="https://github.com/kijai/ComfyUI-SUPIR">ComfyUI-SUPIR</a></li>
<p></p>
<li>Install recommended of <a href="https://github.com/rgthree/rgthree-comfy">rgthree's custom nodes</a> for context input, output.</li>
<p></p>

## **Install:**
Manager -> Install via git URL -> Input https://github.com/NyaamZ/efficiency-nodes-ED <br><br>



## Known bugs
<li>----</li><p></p>
