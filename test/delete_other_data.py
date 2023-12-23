import os

list_dir = ["test/labels", "train/labels", "valid/labels"]
kol_del = 0
kol = 0
name_del_img = list()
kol_classes = dict()
path_to_folder = "C:/Users/dan4i/Downloads/data_ets/"

for i in range(3):
    kol_classes[i] = 0

print(kol_classes)

for kol_dir in range(len(list_dir)):
    name_dir = path_to_folder + list_dir[kol_dir]
    for img_name in os.listdir(name_dir):
        with open(name_dir + "/" + img_name, "r") as file:
            kol += 1
            for line in file:
                num_class = line.split(" ")[0]
                kol_classes[int(num_class)] += 1
                if num_class not in ["0", "2", "3"]:
                    kol_del += 1
                    name_del_img.append([list_dir[kol_dir][:-7], img_name[:-4]])
                    break
            if os.stat(name_dir + "/" + img_name).st_size == 0:
                name_del_img.append([list_dir[kol_dir][:-7], img_name[:-4]])
                print(10)

print(f"All delete {kol_del}")
print(kol_classes)
print(f"All files - {kol}")

# Удаление не нужных файлов
# for elem in name_del_img:
#     try: 
#         os.remove(path_to_folder + elem[0] + "/labels/" + elem[1] + ".txt")
#         os.remove(path_to_folder + elem[0] + "/images/" + elem[1] + ".jpg")
#     except FileNotFoundError as e:
#         # print(e)
#         print(path_to_folder + elem[0] + "/labels/" + elem[1] + ".txt")


# Блок переписывания id классов
# for kol_dir in range(len(list_dir)):
#     name_dir = path_to_folder + list_dir[kol_dir]
#     for img_name in os.listdir(name_dir):
#         with open(name_dir + "/" + img_name, "r") as file:
#             old_data = file.read()
#         new_data = old_data.replace("2", "1")
#         new_data = new_data.replace("3", "2")
        
#         #print(old_data, new_data, sep="\n\n", end="\n-----------------\n")
        
#         with open(name_dir + "/" + img_name, "w") as file:
#             file.write(new_data)