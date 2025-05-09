from PIL import (
    Image,
    ImageOps,
)  # ImageOps 可以用于更高级的操作，例如添加边框以匹配精确尺寸
import os
import glob


def batch_resize_images_preserve_aspect_ratio(
    input_folder,
    output_folder,
    max_width,
    max_height,
    image_types=("*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.tiff"),
):
    """
    批量调整图片尺寸，同时保持宽高比。
    图片会被缩放以适应在 max_width 和 max_height 定义的框内。

    参数:
    input_folder (str): 包含原始图片的文件夹路径。
    output_folder (str): 保存调整后图片的文件夹路径。
    max_width (int): 调整后图片的最大宽度。
    max_height (int): 调整后图片的最大高度。
    image_types (tuple): 要处理的图片文件扩展名元组。
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"创建输出文件夹: {output_folder}")

    image_files = []
    for img_type in image_types:
        # os.path.join 用于正确组合路径
        image_files.extend(glob.glob(os.path.join(input_folder, img_type)))
        # 如果希望递归搜索子文件夹，可以使用 glob.glob(os.path.join(input_folder, '**', img_type), recursive=True)
        # 但要注意，这样保存到 output_folder 时可能需要重建子文件夹结构或展平文件名。

    if not image_files:
        print(f"在 '{input_folder}' 中未找到指定类型的图片。")
        return

    print(f"找到 {len(image_files)} 张图片进行处理...")

    for index, filepath in enumerate(image_files):
        filename = os.path.basename(filepath)
        output_filepath = os.path.join(output_folder, filename)

        try:
            img = Image.open(filepath)
            original_width, original_height = img.size

            # 复制一份图像进行缩略图操作，因为 thumbnail 会直接修改原图像对象
            img_copy = img.copy()

            # Image.thumbnail 会原地修改图像，使其尺寸不超过指定的最大宽度和高度，并保持宽高比
            img_copy.thumbnail(
                (max_width, max_height), Image.Resampling.LANCZOS
            )  # LANCZOS 是高质量的下采样滤镜

            # 保存调整后的图片
            # 如果原始图片有透明通道 (如 PNG)，确保保存时也保留
            if img_copy.mode in ("RGBA", "LA") or (
                img_copy.mode == "P" and "transparency" in img_copy.info
            ):
                img_copy.save(
                    output_filepath, quality=95, optimize=True
                )  # 对于PNG, quality 和 optimize 可能不直接适用，但对于JPG很重要
            else:
                # 对于没有透明通道的图片，可以转换为RGB再保存，以避免某些格式的问题
                img_copy.convert("RGB").save(output_filepath, quality=95, optimize=True)

            print(
                f"({index + 1}/{len(image_files)}) 已处理: {filename} -> 保存到 {output_filepath} (新尺寸: {img_copy.size})"
            )

        except FileNotFoundError:
            print(f"错误: 文件未找到 {filepath}")
        except Exception as e:
            print(f"处理图片 {filename} 时发生错误: {e}")

    print("所有图片处理完毕。")


def batch_resize_images_exact_size(
    input_folder,
    output_folder,
    target_width,
    target_height,
    image_types=("*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.tiff"),
    fill_color=(255, 255, 255, 0),
):
    """
    批量调整图片尺寸到精确的目标尺寸。
    如果原始宽高比与目标不同，图片会被缩放以适应目标尺寸的一边，
    另一边可能会留有空白，这些空白会用 fill_color 填充。

    参数:
    input_folder (str): 包含原始图片的文件夹路径。
    output_folder (str): 保存调整后图片的文件夹路径。
    target_width (int): 调整后图片的精确宽度。
    target_height (int): 调整后图片的精确高度。
    image_types (tuple): 要处理的图片文件扩展名元组。
    fill_color (tuple): 用于填充空白区域的颜色 (R, G, B, A)。默认是透明白色。
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"创建输出文件夹: {output_folder}")

    image_files = []
    for img_type in image_types:
        image_files.extend(glob.glob(os.path.join(input_folder, img_type)))

    if not image_files:
        print(f"在 '{input_folder}' 中未找到指定类型的图片。")
        return

    print(f"找到 {len(image_files)} 张图片进行精确尺寸调整...")

    for index, filepath in enumerate(image_files):
        filename = os.path.basename(filepath)
        output_filepath = os.path.join(output_folder, filename)

        try:
            img = Image.open(filepath)

            # 创建一个新的目标尺寸的背景图层
            background = Image.new("RGBA", (target_width, target_height), fill_color)

            # 复制原始图片以进行缩放，并确保它有Alpha通道以便与背景正确合成
            img_copy = img.copy().convert("RGBA")

            # 保持宽高比缩放
            img_copy.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)

            # 计算粘贴位置（使其居中）
            paste_x = (target_width - img_copy.width) // 2
            paste_y = (target_height - img_copy.height) // 2

            # 将缩放后的图片粘贴到背景中央
            background.paste(
                img_copy, (paste_x, paste_y), img_copy
            )  # 使用img_copy作为mask来处理透明度

            # 保存调整并填充后的图片
            # 如果原始文件名是jpg等不支持透明的格式，最好转为RGB再保存，或者统一保存为PNG
            if filename.lower().endswith((".png", ".gif", ".tiff")):
                background.save(output_filepath, quality=95, optimize=True)
            else:  # 对于jpg, bmp等，转换为RGB
                background.convert("RGB").save(
                    output_filepath, quality=95, optimize=True
                )

            print(
                f"({index + 1}/{len(image_files)}) 已处理: {filename} -> 保存到 {output_filepath} (精确尺寸: {background.size})"
            )

        except FileNotFoundError:
            print(f"错误: 文件未找到 {filepath}")
        except Exception as e:
            print(f"处理图片 {filename} 时发生错误: {e}")
    print("所有图片精确尺寸调整完毕。")


# --- 如何使用 ---
if __name__ == "__main__":
    # ----- 示例 1: 保持宽高比缩放 -----
    print("--- 任务1: 保持宽高比缩放 ---")
    input_directory_aspect = "input_images"  # << 修改这里：你的原始图片文件夹
    output_directory_aspect = (
        "output_images_aspect_ratio"  # << 修改这里：调整后图片的保存文件夹
    )

    # 确保示例文件夹存在
    if not os.path.exists(input_directory_aspect):
        os.makedirs(input_directory_aspect)
        print(f"创建了示例输入文件夹: {input_directory_aspect}，请放入图片后重新运行。")

    # 目标最大尺寸
    desired_max_width = 80
    desired_max_height = 80

    batch_resize_images_preserve_aspect_ratio(
        input_directory_aspect,
        output_directory_aspect,
        desired_max_width,
        desired_max_height,
    )
    print("-" * 30)

    # # ----- 示例 2: 调整到精确尺寸 (带填充) -----
    # print("\n--- 任务2: 调整到精确尺寸 (带填充) ---")
    # input_directory_exact = "input_images"  # << 通常与上面相同，或不同
    # output_directory_exact = (
    #     "output_images_exact_size"  # << 修改这里：调整后图片的保存文件夹
    # )

    # if not os.path.exists(input_directory_exact):  # 再次检查，以防用户只运行此部分
    #     os.makedirs(input_directory_exact)
    #     print(f"创建了示例输入文件夹: {input_directory_exact}，请放入图片后重新运行。")

    # # 目标精确尺寸
    # exact_width = 500
    # exact_height = 500
    # fill_color_bg = (230, 230, 230, 255)  # 浅灰色背景，不透明 (R, G, B, A)

    # batch_resize_images_exact_size(
    #     input_directory_exact,
    #     output_directory_exact,
    #     exact_width,
    #     exact_height,
    #     fill_color=fill_color_bg,
    # )
