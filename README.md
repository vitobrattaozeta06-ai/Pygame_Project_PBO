# Alien Escape

## Deskripsi


Proyek ini kami beri nama Alien Escape. Ini adalah game bertema 2D sidescroll shooter yang mengambil inspirasi utama dari judul terkenal “Metal Slug” dan “Contra” dengan genre yang sama. 
Terdapat 5 level dengan 3 boss dari level 3 - 5. Setelah boss level 5 dikalahkan, ada gameplay tambahan yang berbeda dari game utama yang mengambil tema “Bullet Hell” sebagai extension yang menjadi wave clearing sampai menuju boss sejati.


Anggota Kami:
* Vitobratta Omar Zeta (25051204015)
* Deardo Saragih (25051204057)
* Mohammad Shidqi Fajduani (25051204126)
* Martino Rahardyan Ahmad (25051204226)


Fitur utama yang game ini berikan adalah genrenya sendiri, Sidescroll Shooter. Pemain mengendalikan karakter astronot yang terdampar di planet asing yang harus melawan alien dengan berbagai macam alat loot tersedia di map. 
Kemudian ada lanjutannya, Spaceship Bullet Hell, yang hanya bisa diakses setelah berhasil melewati level 5. Sekarang, player mengendalikan pesawat dan harus mengalahkan armada alien sambil menghindari tiap peluru sampai boss terakhir nya.


Project ini dijalankan cukup mudah dengan membuka source code dan langsung run. Karena dibuat murni dengan Pygame dan beberapa asset yang di import dari sumber luar. 

Implementasi OOP/PBO :
- Inheritance: Pada bagian Enemy Colors. Dimana semua instance objek Enemy mewarisi dictionary mapping warna dari blueprint kelasnya masing-masing tanpa perlu di definisikan ulang setiap kali instansi
- Encapsulation : Player Class. Kelas Player menyatukan data sensitif (posisi, HP, peluru, senjata aktif) dan behavior yang memanipulasi data tersebut dalam satu unit yang terlindungi. Main loop jadi tidak perlu mengubah data secara manual.
- Abstraction : Platform & Loot Generation. Kompleksitas algoritma prosedural (perhitungan posisi X, Y dan probabilitas spawn platform kedua) disembunyikan. Jadi main loop hanya memanggil ‘PlatformerLevel(level_num)’ dan tidak perlu tahu detail kecil lain
- Polymorphism : Duck typing pada method ‘update()’ dan ‘draw()’ pada PlatformerScene dan SpaceShooterScene. Main loop dapat memanggil method secara seragam tanpa perlu mengecek tipe objek secara eksplisit. Seperti penanganan entity Enemy dan Boss.

Screenshot Tampilan Program:
<img width="372" height="243" alt="image" src="https://github.com/user-attachments/assets/5b079bda-095d-41fe-b7aa-faddf62bf54a" />
<img width="376" height="246" alt="image" src="https://github.com/user-attachments/assets/a1ac8370-dbab-45bb-8981-7138440debbb" />
<img width="470" height="308" alt="image" src="https://github.com/user-attachments/assets/2e1ef996-ef8e-4973-b99b-7d38634e9b70" />
<img width="480" height="314" alt="image" src="https://github.com/user-attachments/assets/60538dc5-2772-43aa-b711-5bc39a43b250" />
