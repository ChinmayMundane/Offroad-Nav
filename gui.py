import tkinter as tk
from tkinter import filedialog, simpledialog
from PIL import Image, ImageTk
from skimage.segmentation import slic
from skimage.segmentation import mark_boundaries
import numpy as np
import cv2
import os

class SuperpixelGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Superpixel GUI")

        self.image_folder = ""
        self.image_paths = []
        self.current_image_index = 0
        self.image = None
        self.superpixels = None
        self.save_name = ""

        self.open_button = tk.Button(self.master, text="Open Folder", command=self.open_folder)
        self.open_button.pack()

        self.save_button = tk.Button(self.master, text="Save", command=self.ask_save_name, state=tk.DISABLED)
        self.save_button.pack()

        self.compactness_var = tk.IntVar()
        self.compactness_scale = tk.Scale(self.master, from_=0, to=100, length=300, orient=tk.HORIZONTAL, label="Compactness", variable=self.compactness_var)
        self.compactness_scale.set(25)
        self.compactness_scale.pack()

        self.num_superpixels_var = tk.IntVar()
        self.num_superpixels_scale = tk.Scale(self.master, from_=5, to=200, length=300, orient=tk.HORIZONTAL, label="Number of Superpixels", variable=self.num_superpixels_var)
        self.num_superpixels_scale.set(100)
        self.num_superpixels_scale.pack()

        self.generate_button = tk.Button(self.master, text="Generate Superpixels", command=self.generate_superpixels)
        self.generate_button.pack()

        self.num_segments_label = tk.Label(self.master, text="Actual number of superpixels: -")
        self.num_segments_label.pack()

        self.original_image = None  # New instance variable

        self.color_labels = {
            1: ("void", "#000000"), 2: ("dirt", "#FF0000"), 3: ("grass", "#00FF00"), 4: ("trees", "#0000FF"),
            5: ("pole", "#FFFF00"), 6: ("water", "#00FFFF"), 7: ("sky", "#FF00FF"), 8: ("vehicle", "#800080"),
            9: ("object", "#FFA500"), 10: ("asphalt", "#808080"), 11: ("build", "#FFFF80"), 12: ("log", "#7CFC00"),
            13: ("person", "#FFC0CB"), 14: ("fence", "#808000"), 15: ("bush", "#228B22"), 16: ("concrete", "#A9A9A9"),
            17: ("barrier", "#8B0000"), 18: ("puddle", "#ADD8E6"), 19: ("mud", "#8B4513"), 20: ("rubber", "#800080")
        }

        self.color_buttons = []
        button_frame = tk.Frame(self.master)
        button_frame.pack(side=tk.RIGHT)

        for label_id, (label_name, label_color) in self.color_labels.items():
            color_button = tk.Button(button_frame, text=label_name, bg=label_color,
                                    command=lambda id=label_id: self.select_label(id))
            row = label_id // 2
            col = label_id % 2
            color_button.grid(row=row, column=col, padx=5, pady=5)
            self.color_buttons.append(color_button)

        self.canvas = tk.Canvas(self.master, width=800, height=600)
        self.canvas.pack()

        self.selected_label = None
        self.selected_color = None

        self.segment_labels = {}

        self.canvas.bind("<Button-1>", self.assign_label)  # Bind the label assignment function to the left button click

    def open_folder(self):
        self.image_folder = filedialog.askdirectory()
        if self.image_folder:
            self.image_paths = [os.path.join(self.image_folder, filename) for filename in os.listdir(self.image_folder) if
                                filename.endswith(('.jpg', '.png'))]
            if self.image_paths:
                self.load_image(0)

    def load_image(self, index):
        if 0 <= index < len(self.image_paths):
            image_path = self.image_paths[index]
            self.original_image = Image.open(image_path)  # Store the original opened image
            self.image = self.original_image.resize((800, 600))  # Resize the image to fit in the canvas
            self.show_image()
            self.current_image_index = index

            self.save_button.configure(state=tk.DISABLED)

    def show_image(self):
        if self.image:
            tk_image = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
            self.canvas.image = tk_image

    def generate_superpixels(self):
        compactness = self.compactness_var.get()
        num_segments = self.num_superpixels_var.get()
        self.superpixels = slic(np.array(self.image), n_segments=num_segments, compactness=compactness)
        self.show_superpixels()
        actual_segments = np.unique(self.superpixels)
        self.num_segments_label.configure(text="Actual number of superpixels: " + str(len(actual_segments)))
        self.save_button.configure(state=tk.DISABLED)

    def show_superpixels(self):
        if self.image and self.superpixels is not None:
            segmented_image = mark_boundaries(np.array(self.image), self.superpixels)
            segmented_image = (segmented_image * 255).astype(np.uint8)
            segmented_image = Image.fromarray(segmented_image)

            tk_image = ImageTk.PhotoImage(segmented_image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
            self.canvas.image = tk_image

    def select_label(self, label_id):
        self.selected_label = label_id
        self.selected_color = self.color_labels[label_id][1]

    def assign_label(self, event):
        if self.selected_label is None or not self.image:
            return

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        segment_id = self.superpixels[int(y), int(x)]

        # Segment the superpixel using the color of the selected label
        label_color = self.selected_color
        mask = (self.superpixels == segment_id)
        segmented_image = np.array(self.image)
        segmented_image[mask] = tuple(int(label_color[i:i + 2], 16) for i in (1, 3, 5))
        self.image = Image.fromarray(segmented_image)

        # Assign the label ID to the segment ID
        self.segment_labels[segment_id] = self.selected_label

        # Update the displayed superpixel image with the segmented label
        self.show_superpixels()

        # Check if all superpixels have been labeled
        if len(self.segment_labels) == len(np.unique(self.superpixels)):
            self.save_button.configure(state=tk.NORMAL)

    def ask_save_name(self):
        save_name = simpledialog.askstring("Save Image", "Enter a name for saving the images:")
        if save_name:
            self.save_name = save_name.strip()
            self.save_images()

    def save_images(self):
        save_folder = "images"
        os.makedirs(save_folder, exist_ok=True)
        original_save_path = os.path.join(save_folder, f"{self.save_name}.png")
        self.original_image.save(original_save_path)  # Save the original image

        color_labels_folder = "color_labels"
        os.makedirs(color_labels_folder, exist_ok=True)
        color_save_path = os.path.join(color_labels_folder, f"{self.save_name}.png")
        labeled_image = self.label_image()
        labeled_image.save(color_save_path)

        labels_folder = "labels"
        os.makedirs(labels_folder, exist_ok=True)
        gray_save_path = os.path.join(labels_folder, f"{self.save_name}.png")
        gray_array = self.get_gray_array()
        cv2.imwrite(gray_save_path, gray_array)

        self.segment_labels = {}  # Clear the segment labels for the next image
        self.current_image_index += 1
        self.load_image(self.current_image_index)  # Load the next image

    def label_image(self):
        labeled_image = np.array(self.image)
        for segment_id, label_id in self.segment_labels.items():
            mask = (self.superpixels == segment_id)
            label_color = self.color_labels[label_id][1]
            labeled_image[mask] = tuple(int(label_color[i:i + 2], 16) for i in (1, 3, 5))

        return Image.fromarray(labeled_image)

    def get_gray_array(self):
        image_shape = self.image.size
        gray_array = np.zeros((image_shape[1], image_shape[0]), dtype=np.uint8)
        for segment_id, label_id in self.segment_labels.items():
            gray_array[self.superpixels == segment_id] = label_id

        return gray_array

    def next_image(self):
        self.segment_labels = {}  # Clear the segment labels for the next image
        self.current_image_index += 1
        self.load_image(self.current_image_index)  # Load the next image


if __name__ == "__main__":
    root = tk.Tk()
    gui = SuperpixelGUI(root)
    root.mainloop()

