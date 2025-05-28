**[[한국어]](https://github.com/NyaamZ/efficiency-nodes-ED/blob/main/README_KR.md)**

✨🍬An extension pack that adds functionality to Efficiency Nodes, enhancing the user experience. The original version can be found at: https://github.com/jags111/efficiency-nodes-comfyui 🍬

**Efficiency Nodes 💬ExtendeD (V8)**
=======

　

## Workflow Examples:

- ##### Main Workflow

  <div id="wrap">
      <div class="img-wrap"><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/workflows/workflow_Main.png" alt=""></div>
      <div class="txt-wrap"><p>(EXIF included)</p></div>
  </div>

- ##### Regional Workflow

  <div id="wrap">
      <div class="img-wrap"><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/workflows/workflow_regional.png" alt=""></div>
      <div class="txt-wrap"><p>(EXIF included)</p></div>
  </div>

- ##### Flux Workflow

  <div id="wrap">
      <div class="img-wrap"><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/workflows/workflow_flux.png" alt=""></div>
      <div class="txt-wrap"><p>(EXIF included)</p></div>
  </div>



　

## **Basic Overview:**



- ## Context:

  Unlike the original Efficiency Nodes, 💬ED Nodes exchange the <code>context</code> link.

  Think of the `context` link as a bundle combining multiple links like `model`, `clip`, `vae`, `conditioning`, etc.

  

  - When creating workflows, you might end up with spaghetti-like connections like this: 

    <p align="left">
      <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0001.jpg" width="600" style="display: inline-block;">
    </p>

  - Using the `context` link simplifies it:

    <p align="left">
      <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0002.png" width="600" style="display: inline-block;">
    </p>

  - It’s not limited to 💬ED Nodes - other nodes can use it too.

    <div id="wrap">
        <div class="img-wrap"><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0003.png" alt=""></div>
        <div class="txt-wrap"><p>(EXIF included)</p></div>
    </div>

  - The `context` link output by Efficient Loader 💬ED includes the following:

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
                        <td>Instead contains batch_size</td>
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

　

- ## Checkpoint, LoRA, and Embedding Thumbnails:

  Efficient Loader 💬ED, LoRA Stacker 💬ED, and Embedding Stacker 💬ED display thumbnails when selecting models.

   

  - Thumbnail Style

    <p><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0006.png" alt="" width="600" style="display: inline-block;"></p>

  - Tree Style

    <p><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0007.png" alt="" width="600" style="display: inline-block;"></p>

  - You can select the style in: Settings > pysssss > Combo++ > Lora/Checkpoint Loader Display Mode

    <p align="left">
      <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0008.png" width="600" style="display: inline-block;">
    </p>

  - Thumbnails may not appear initially. To enable them:

    Right-click on Efficient Loader 💬ED or LoRA Stacker 💬ED >  <code>🔍 View model info...</code>

     <p><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0017.png" width="500" style="display: inline-block;"></p>

    Click `Use as preview` in the red section to save it. (You can also manually specify the filename as `MODEL NAME.jpg` or `.png`)

    

　


- ## Wildcards:

  Efficiency Nodes 💬ED supports wildcards.

   

  - ### Usage

    - Use `Select to add wildcard` in Get booru Tag 💬ED to easily add wildcards.

      <p align="left">
        <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0009.png" width="400" style="display: inline-block;">
      </p>

    - Wildcards are shared with Impact Pack’s wildcards: `ComfyUI\custom_nodes\comfyui-impact-pack\wildcards`
    - All standard wildcard syntax is supported, but nested wildcards and LoRAs are not.
    - Wildcard encoding is handled by Efficient Loader 💬ED, so Get booru Tag 💬ED is not strictly required.
    - Supports comments: `#`, `//`, `/* */`.

    

  - ### Sequential Wildcards

    - In Get booru Tag 💬ED, write `__wildcard__#ASC0` in the `text_b` field.

      <p align="left">
        <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0010.png" width="400" style="display: inline-block;">
      </p>

    - `#ASCXX` iterates upward from the specified number (stops at max).

    - `#DSCXX` iterates downward from the specified number (stops at 0).
      (If unsure of the max, use `#DSC1000` as a rough estimate.)

    - `#FIXXX` fixes the value

    - Sequential wildcards are only available via Get booru Tag 💬ED.
    

　

- ## Regional Prompt:

  Regional prompts allow different prompts for specific areas. ([Regional Workflow](https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/workflows/workflow_regional.png))

  Requires installation of [**A8R8 ComfyUI Nodes**](https://github.com/ramyma/A8R8_ComfyUI_nodes).

  

  - ### Regional Prompt - Text 2 Image

    1. Right-click Regional Stacker 💬ED, input aspect ratio, and click `Create empty image`. This auto-fills dimensions in Efficient Loader 💬ED and loads an empty image into `Load Image` connected to Regional Script 💬ED.

       <p align="left">
         <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0011.png" width="300" style="display: inline-block;">
       </p>

    2. Define regions with masks and write prompts. (Attach LoRA Stacker 💬ED if needed.)

       <p align="left">
         <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0012.jpg" width="800" style="display: inline-block;">
       </p>

    3. Write a base prompt and execute the queue.

       <p align="left">
         <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0013.png" width="700" style="display: inline-block;">
       </p>

    4. Result:

       <div id="wrap">
           <div class="img-wrap"><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0014.png" alt="" width="400" style="display: inline-block;"></div>
           <div class="txt-wrap"><p>(EXIF included)</p></div>
       </div>
        
       

  - ### Regional Prompt - Image 2 Image

    1. If [ComfyUI-ImageGallery-ED](https://github.com/NyaamZ/ComfyUI-ImageGallery-ED) is installed, double-clicking an image opens the gallery.

       <p align="left">
         <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0015.png" width="600" style="display: inline-block;">
       </p>

    2. Click the red section to load the current image into `Load Image` connected to Regional Script 💬ED.

    3. Define masks, write prompts, and queue.
    

　

- ## ControlNet:

  Attach `Control Net Stacker` to Efficient Loader 💬ED to use ControlNet.

  <p align="left">
    <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0016.png" width="800" style="display: inline-block;">
  </p>

  ControlNet and Regional Script can be used simultaneously.

　

- ## Get booru Tag:

  1. If you find a good image on Danbooru or Gelbooru, copy its URL:

     <p align="left">
       <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0018.jpg" width="600" style="display: inline-block;">
     </p>

  2. Paste it into the `url` field of `Get booru Tag 💬ED`:

     <p><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0019.png" width="500" style="display: inline-block;"></p>

  3. Tags are extracted in real-time (comments are marked with `/* */`):

     <p><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0020.png" width="500" style="display: inline-block;"></p>

  4. From 0.8.5, a new widget called <code>Group tags by category</code> has been added to the Get booru Tag 💬ED. When there are too many tags like the example below, it can become overwhelming.

     <p><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0042.png" width="500" style="display: inline-block;"></p>

  5. Clicking it will group the tags by category.

     <p><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0043.png" width="500" style="display: inline-block;"></p>

  6. The inputs `text_a` and `text_c` are simply combined and output as `text`.

     <p><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0044.png" width="500" style="display: inline-block;"></p>

　

- ## Set_seed_cfg_sampler:

  Nodes like `KSampler (Efficient) 💬ED`, `FaceDetailer 💬ED`, and `Ultimate SD Upscale 💬ED` include the `set_seed_cfg_sampler` widget.

  Configure `seed`, `cfg`, `sampler`, and `scheduler` once in `Efficient Loader 💬ED` - no need to set them repeatedly.

  - `from context`: Uses settings from `context` output by `Efficient Loader 💬ED`.
  - `from node to ctx`: Exports current node settings to `context`.
  - `from node only`: Uses current node settings without saving to `context`.

  <p align="left">
    <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0023.png" width="400" style="display: inline-block;">
  </p>

　

- ## XY Plot:

  XY plots help find optimal settings (e.g., for `cfg` or `sampler`).

  1. Right-click `KSampler (Efficient) 💬ED` > `Add script` > `XY plot`.

     <p align="left">
       <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0024.png" width="500" style="display: inline-block;">
     </p>
  
  2. Set `ksampler_output_image` to `Plot`.

     Right-click `XY plot` > `Add X input` > `XY Input: Sampler/Scheduler`

     Right-click `XY plot` > `Add Y input` > `XY Input: Sampler/Scheduler`

     <p><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0025.png" width="500" style="display: inline-block;"></p>

  3. Running the queue displays optimal settings at a glance:

     <p><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0026.jpg" width="700" style="display: inline-block;"></p>

　

- ## Refiner script:

  Adapted from `KSampler (Advanced)`.

  

  - ### Uses Cases

    1. Hires FIx

       - Faster and less distortion compared to `Ultimate SD Upscale 💬ED`.
       
    2. Refining with Different Models:
       - Adjust colors, textures, etc.
    
    
    
  - ### Hires Fix with Refiner Script
  
    1. Upscale 2x using `Load Image 💬ED` (with `upscale_method` and `keep_proportions`).
  
       (Setting <code>keep_proportions</code> to 2x automatically adjusts the <code>width</code> and <code>height</code> without needing to input them manually.)
  
       <p align="left">
         <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0035.png" width="400" style="display: inline-block;">
       </p>
  
    2. Right-click `KSampler (Efficient) 💬ED` > `Add script` > `Refiner Script 💬ED`.
  
       Set `steps`, `denoise`, and `start_at_step`.
  
       <p align="left">
         <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0036.png" width="600" style="display: inline-block;">
       </p>

    3. From 0.8.5, you can attach the LoRA Stacker 💬ED to the Refiner Script 💬ED.

       (This is an additional LoRA used during refining. If a different model is loaded, only this LoRA will be used. For example, if the character becomes distorted or the proportions look off after Hires Fix, using a LoRA like [this one](https://civitai.com/models/1461427) can help improve the result.)

       <p align="left">
         <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0044.png" width="600" style="display: inline-block;">
       </p>

    4. Run the queue.
  
       <div id="wrap">
           <div class="img-wrap"><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0037.png" alt="" width="400" style="display: inline-block;"></div>
           <div class="txt-wrap"><p>(EXIF included)</p></div>
       </div>

　



- ## 💬ED Node Descriptions:

  <details>
      <summary><b>Efficient Loader 💬ED</b></summary>
  <ul>
          <p></p>
      <li>Combines Load Checkpoint, CLIP Set Last Layer, Empty Latent Image, and Repeat Latent Batch into one node with enhanced functionality.<br>
        <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0021.png" width="250" style="display: inline-block;">
        </li>
      <p></p>
      <li>Switch between <code>Txt2Img</code>, <code>Img2Img</code>, and <code>Inpaint</code> with one click.<br><i>(<code>Txt2Img</code> mode auto-sets denoise=1 in connected KSampler (Efficient) 💬ED.)</i><br>
        <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/0f8549b8-cbe0-4662-b922-df21545e2d8f" width="250" style="display: inline-block;">
        </li>
      <p></p>
      <li><code>Inpaint(MaskDetailer)</code> mode:  Uses Impact Pack’s MaskDetailer for better quality (avoids degradation)<br>
        <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/5b04b764-f995-4350-b897-e42041686a2d" width="250" style="display: inline-block;">
        </li>
      <li>Saves seed, cfg, sampler, and scheduler to <code>context</code> for reuse in other nodes.</li>
      <p></p>
      <li>Right-click menu:<br>
          <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/47995eca-94fb-4e52-b77b-2a53e9f292d0" width="150" style="display: inline-block;">
          <p> <code>🔍 View model info...</code> Displays model's info.<br>          
            <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/f7cf378c-cd8a-49cb-9389-5681caacf130" width="250" style="display: inline-block;"><br>
            <i>(It is recommended to click <code>Use as preview</code> the first time.)</i><br></p>
          <p> <code>📐 Aspect Ratio...</code> Auto-fills <code>image_width</code>/<code>image_height</code> with preset ratios (◆ = recommended).<br>
            <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/f92fdd33-ddcb-4b42-904c-4c67a52e4aa0" width="250" style="display: inline-block;"><br></p>
      </li>
      <p></p>
      <li>Tiled VAE Encoding<br>
          <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/b160f24f-09f6-460f-a1a4-e906077ff61b" width="300" style="display: inline-block;"><br>
            - In the Property Panel, setting <code>Use tiled VAE encode</code> to true enables the use of Tiled VAE<br>
      </li>
      <p></p>
      <li>Supports <code>lora_stack</code> and <code>cnet_stack</code> connections.</li>
      <p></p>
      <li>In the Property Panel, you can configure the prompt <a href="https://github.com/BlenderNeko/ComfyUI_ADV_CLIP_emb">encoding method</a> using <code>Token normalization</code> and <code>Weight interpretation</code>.</li>
      <p></p>
      <li><code>Use Latent Rebatch</code> (default: true) splits batch processing for stability.</li>
      <p></p>
      <li><code>Clip skip=0</code> disables CLIP skip.</li>
      <p></p>
  </ul>
  </details>
  <details>
      <summary><b>KSampler (Efficient) 💬ED</b></summary>
  <p></p>
  - Modified to accept <code>context</code> input. Outputs sampled images to <code>CONTEXT</code> and <code>OUTPUT_IMAGE</code>; <code>steps</code> to <code>STEPS_INT</code>.<p></p>
  <p align="left">
    <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0022.png" width="500">
  </p>
      <p></p>   
      <p></p>
      <li>Tiled VAE Decode<br>
        - Enable <code>Use tiled VAE decode</code> in Properties Panel for large images<br>
      </li>
  </details>
  <details>
      <summary><b>Inpaint(MaskDetailer) Mode</b></summary>
  <p></p>
  - When you select Inpaint (MaskDetailer) mode in Efficient Loader 💬ED, the Efficient Sampler 💬ED switches to Mask Detailer mode.<p></p>
  - Integrates Impact Pack’s MaskDetailer for good quality.<p></p>
  <p align="left">
    <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/09e4dfd2-e1f7-4118-8bb2-2adcdca236d0" width="400">
  </p>
  - Can configure <code>drop size, cycle, inpaint model, noise mask feather</code> in Properties Panel.<p></p>
  </details>
  <details>
      <summary><b>Load Image 💬ED</b></summary>
  <p></p>
  <p align="left">
    <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0026.png" width="400">
  </p>
  - Combines image loading and upscaling. Extracts prompt text from metadata.<p></p>
  <li>Upscale: Select method in <code>upscale_method</code>, input <code>width</code>/<code>height</code>.<br>
    <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0027.png" width="400"><br>
  </li>
  <li>You can upscale an image while preserving its aspect ratio using <code>keep_proportions</code>.</li>
  <li>Values like 1.5x, 2x, or 3x ignore the <code>width</code> and <code>height</code> settings and automatically adjust the dimensions according to the aspect ratio.</li>
  <li><code>based on width</code> keeps the specified <code>width</code> and automatically adjusts the height according to the aspect ratio.</li>
  <p></p>
  - When the queue runs, the prompt and seed are displayed as shown below.<br>
    <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/5b18adb0-5e8e-4cc0-963d-287cb5d19e38" width="700"><br>
  </details>
  <details>
  <p></p>
      <summary><b>Save Image 🔔ED</b></summary>
  <p></p>
  <p align="left">
    <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/8e730793-1c61-4152-90a7-343de68d16a6" width="300">
  </p>
  - Modified Save Image node with <code>context</code> input and audible notification.<p></p>
  <li>Toggle sound in Properties Panel (Play sound, Sound Volume 0–1).<br>
    <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/946fcc7f-6a06-4377-bfde-4516d616bd55" width="500"><br>
  </li>
  <p></p>
  <li>To change the notification sound, replace the file at <code>efficiency-nodes-comfyui\js\assets\notify.mp3</code>.</li>
  </details>
  <details>
    <p></p>
    <summary><b>LoRA Stacker 💬ED</b></summary>
    <p></p>
    <p align="left">
    <img src="https://github.com/user-attachments/assets/a8b132f3-65d5-4bc9-a44d-566b1e9a4b33" width="300">
    </p>
    - Loads up to 9 LoRAs simultaneously.<p></p>
    <p></p>
    <li>Folder-based submenus with previews <br>
      <img src="https://github.com/user-attachments/assets/2e98c870-1d8f-407d-83da-953c6ab13e87" width="300"><br>
    </li>
    <p></p>
    <li><code>🔍 View model info...</code> displays trained trigger words.<br>
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
    - As a simple feature, Efficient Loader 💬ED appends embedding strings to the end of both positive and negative prompts.<br>
    <li>Works only with Efficient Loader 💬ED.</li><br>
    <li>You can view Embedding info by clicking <code>🔍 View model info...</code>.</li><br>
    <p></p>
  </details>
  <details>
    <p></p>
    <summary><b>Wildcard Encode 💬ED</b></summary>
    <p></p>
    <p align="left">
    <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0028.png" width="400">
    </p>
    - The node that handles wildcards when Efficient Loader 💬ED's <code>Use Latent Rebatch</code> is set to true.<br>
    <i>(It was created to apply wildcards separately for each batch.)</i><br>
    <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0029.png" width="600">
    <p></p>
    <li>It looks similar to the Context node and performs the same function.</li>
    <p></p>
    <li>If you set <code>Turn on Apply Lora</code> to true in the Properties Panel, you can delay the timing of Lora application.<br>
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
    - A modified version of the TIPO node that can accept <code>context</code> as an input.<p></p>
    - This is a node that randomly creates prompts. For more details, refer to <a href="https://github.com/KohakuBlueleaf/z-tipo-extension">this link</a>.<p></p>
    - To use this, you need to install z-tipo-extension.<p></p>
  </details>
  <details>
    <p></p>
    <summary><b>Regional Stacker 💬ED, Regional Script 💬ED</b></summary>
    <p></p>
    <p align="left">
    <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0038.png" width="500">
    </p>
    - Nodes used for regional prompts.<p></p>
    - The <code>url</code> in Regional Script 💬ED functions the same as the <code>url</code> in Get booru Tag 💬ED. It can get tags from Gelbooru or Danbooru.<p></p>
    - Regional Script 💬ED supports wildcard input.<p></p>
  </details>
  <details>
    <p></p>
    <summary><b>Refiner Script 💬ED</b></summary>
    <p></p>
    <p align="left">
    <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0039.png" width="300">
    </p>
    - A node that adds a refining process to the KSampler (Efficient) 💬ED node.<p></p>
    - By attaching a Load Checkpoint node, you can perform refining with a different model as shown below.<br><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0040.png" width="500"><p></p>
    - Setting <code>ignore_batch_size</code> to true means the operation runs only once, ignoring <code>ibatch_size</code>.<p></p>
    - <code>do_refine_only</code> set to true means only refining is done; set to false means the image is sampled first, then refined.<p></p>
  </details>
  <details>
    <p></p>
    <summary><b>Int Holder 💬ED</b></summary>
    <p></p>
    <p align="left">
    <img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0033.png" width="400">
    </p>
    - A node that remembers the <code>steps</code> used when generating an image with KSampler (Efficient) 💬ED and stores it in <code>context</code> when running Hires Fix.<p></p>
    - If <code>steps</code> exists in <code>context</code>, FaceDetailer 💬ED and Ultimate SD Upscale 💬ED will prioritize using it.<p></p>
    - A node created to avoid the hassle of entering <code>steps</code> manually each time.<p></p>
  </details>
  <details>
    <p></p>
    <summary><b>FaceDetailer 💬ED</b></summary>
    <p></p>
    <p align="left">
    <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/3c79367f-e2f7-4f3c-bffe-48be9a6627c9" width="250">
    </p>
    - FaceDetailer addon from Impact pack.<p></p>
    - A modified version that can accept <code>context</code> as input.<p></p>
  </details>
  <details>
    <p></p>
    <summary><b>MaskDetailer 💬ED</b></summary>
    <p></p>
    <p align="left">
    <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/87bbd155-8b06-423d-b8e8-04a8f55b223d" width="250">
    </p>
    - MaskDetailer addon from Impact pack.<p></p>
    - A modified version that can accept <code>context</code> as input.<p></p>
  </details>
  <details>
    <p></p>
    <summary><b>Detailer (SEGS) 💬ED</b></summary>
    <p></p>
    <p align="left">
    <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/c538b972-0e14-4b53-861d-ed0f78da0248" width="250">
    </p>
    - Detailer (SEGS) addon from Impact pack.<p></p>
    - A modified version that can accept <code>context</code> as input.<p></p>
  </details>
  <details>
    <p></p>
    <summary><b>Ultimate SD Upscale 💬ED</b></summary>
    <p></p>
    <p align="left">
    <img src="https://github.com/jags111/efficiency-nodes-comfyui/assets/43065065/34fc20e4-8577-4716-9197-f63a31a6a31f" width="200">
    </p>
    - Ultimate SD Upscale addon.<p></p>
    - A modified version that can accept <code>context</code> as input.<p></p>
  </details>
  <details>
    <p></p>
    <summary><b>SUPIR 💬ED</b></summary>
    <p></p>
    <p align="left">
    <img src="https://github.com/user-attachments/assets/ef20c2cf-e0fa-4505-a432-50a97d0cb7f4" width="400">
    </p>
    - An addon for ComfyUI-SUPIR. While SUPIR excels at High-res Fix, it normally requires six nodes, but this addon reduces them to just two.<p></p>
    - SUPIR requires a dedicated model. For downloading the model and more details, refer to <a href="https://github.com/kijai/ComfyUI-SUPIR">this link</a><p></p>
    - Installation of <a href="https://github.com/kijai/ComfyUI-SUPIR">ComfyUI-SUPIR</a> is required.<p></p>
    - Example video<p></p>
  <video  src="https://github.com/kijai/ComfyUI-SUPIR/assets/40791699/5cae2a24-d425-462c-b89d-df7dcf01595c"  controls>Example video </video> 
  </details>

　

## **Installation:**
1. In Manager > Custom Node Manager > Search, install the following:

   [**ComfyUI Impact Pack**](https://github.com/ltdrdata/ComfyUI-Impact-Pack)  (Optional)

   [**ComfyUI Impact Subpack**](https://github.com/ltdrdata/ComfyUI-Impact-Subpack)  (Optional)

   [**ComfyUI-Custom-Scripts**](https://github.com/pythongosssss/ComfyUI-Custom-Scripts)  (Absolutely Required!)

   [**ComfyUI_UltimateSDUpscale**](https://github.com/ssitu/ComfyUI_UltimateSDUpscale)  (Optional)

   [**rgthree-comfy**](https://github.com/rgthree/rgthree-comfy)  (Optional)

   [**efficiency-nodes-comfyui**](https://github.com/jags111/efficiency-nodes-comfyui)  (Absolutely Required!)

   [**efficiency-nodes-ED**](https://github.com/NyaamZ/efficiency-nodes-ED)  (This Nodes)

   [**ComfyUI-ImageGallery-ED**](https://github.com/NyaamZ/ComfyUI-ImageGallery-ED)  (It's more convenient when used together)

   [**ComfyUI_BiRefNet_ll**](https://github.com/lldacing/ComfyUI_BiRefNet_ll)  (Optional)

   [**z-tipo-extension**](https://github.com/KohakuBlueleaf/z-tipo-extension)  (Optional)

   [**A8R8 ComfyUI Nodes**](https://github.com/ramyma/A8R8_ComfyUI_nodes)  (Optional)


2. After installation > restart >
   Run <code>ComfyUI\custom_nodes\efficiency-nodes-ED\start.bat</code>

　

## ***How to fix errors***

- The issue where the <code>steps</code> in FaceDetailer 💬ED and Ultimate SD Upscale 💬ED gets fixed unexpectedly is caused by this node: Int Holder 💬ED.

    <p><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0034.png" width="250" style="display: inline-block;"></p>
    
    This node remembers the <code>steps</code> used when generating an image with Sampler (Efficient) 💬ED and stores it in <code>context</code> during Hires Fix. Since FaceDetailer 💬ED and Ultimate SD Upscale 💬ED prioritize using the <code>steps</code> stored in <code>context</code>, it avoids having to input steps manually every time.
    
    If this behavior is unnecessary or if you want to input <code>steps</code> manually, simply mute this node (Ctrl+M) or delete it.


　

## Known bug

- There is a bug in [**efficiency-nodes-comfyui**](https://github.com/jags111/efficiency-nodes-comfyui). If used as is, it causes a <code>Cannot redefine property</code> error. After updating, be sure to run <code>start.bat</code> to fix this.
  
- There is a bug where clicking <code>🔍 View model info...</code> fails to find the model on civitai.com as shown below.
  
   <p><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0041.png" width="400" style="display: inline-block;"></p>
   
    This issue happens because the hash value doesn't match.
   
   <p><img src="https://raw.githubusercontent.com/NyaamZ/efficiency-nodes-ED/refs/heads/main/html_resource/0042.jpg" width="800" style="display: inline-block;"></p>
   
   On [civitai.com](https://unsafelink.com/https://civitai.com/), click the highlighted red area to copy the hash value.
   
   Open <code>ComfyUI\models\checkpoints\MODEL_NAME.sha256</code> with a text editor and overwrite its contents with the copied hash value.

