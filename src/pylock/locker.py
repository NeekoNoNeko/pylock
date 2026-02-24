import json
import os
import random
import shutil
import string
import sys
import tarfile
import tempfile
from pathlib import Path

import pyzipper


def get_program_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent


def generate_random_string(length: int = 20) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def update_ciphertext_log(
    original_name: str, encrypted_name: str, log_path: str | Path
):
    log_path = Path(log_path)

    if not log_path.exists():
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

    if log_path.exists():
        with open(log_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(
        {
            "original_name": original_name,
            "encrypted_name": encrypted_name,
        }
    )

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def lock_file(
    target_path: str | Path, password: str, output_dir: Path | str | None = None
):
    target_path = Path(target_path)
    if not target_path.exists():
        raise FileNotFoundError(f"Target file not found: {target_path}")

    if output_dir is None:
        output_dir = target_path.parent
    else:
        output_dir = Path(output_dir)

    original_name = target_path.name

    encrypted_name = generate_random_string(20)
    zip_random_name = generate_random_string(20)
    cipher_random_name = generate_random_string(20)
    cipher_file_name = f"{cipher_random_name}.ciper"

    cipher_content = original_name.encode("utf-8")
    cipher_temp_path = output_dir / cipher_file_name
    with open(cipher_temp_path, "wb") as f:
        f.write(cipher_content)

    zip_path = output_dir / f"{zip_random_name}.zip"
    with pyzipper.AESZipFile(zip_path, "w") as zf:
        zf.setpassword(password.encode("utf-8"))
        zf.setencryption(pyzipper.WZ_AES)
        zf.write(target_path, encrypted_name)
        zf.write(cipher_temp_path, cipher_file_name)

    txt_file_path = output_dir / f"{original_name}.txt"
    with open(txt_file_path, "w", encoding="utf-8") as f:
        pass

    os.remove(cipher_temp_path)

    tar_path = output_dir / f"{encrypted_name}.tar"
    with tarfile.open(tar_path, "w") as tf:
        tf.add(zip_path, arcname=f"{zip_random_name}.zip")
        tf.add(txt_file_path, arcname=f"{original_name}.txt")

    os.remove(zip_path)
    os.remove(txt_file_path)

    ciphertext_log_path = get_program_dir() / "cipertext.json"
    update_ciphertext_log(original_name, encrypted_name, ciphertext_log_path)

    return {
        "original_name": original_name,
        "encrypted_name": encrypted_name,
        "tar_path": str(tar_path),
    }


def unlock_file(tar_path: str | Path, password: str) -> dict:
    tar_path = Path(tar_path)
    if not tar_path.exists():
        raise FileNotFoundError(f"TAR file not found: {tar_path}")

    output_dir = tar_path.parent

    with tempfile.TemporaryDirectory() as temp_dir:
        with tarfile.open(tar_path, "r") as tf:
            tf.extractall(temp_dir)

        extracted_files = list(Path(temp_dir).iterdir())

        zip_file = None
        for f in extracted_files:
            if f.suffix == ".zip":
                zip_file = f
                break

        if zip_file is None:
            raise FileNotFoundError("ZIP file not found in TAR")

        zip_temp = Path(temp_dir) / "temp.zip"
        shutil.copy(zip_file, zip_temp)
        os.remove(zip_file)

        extract_dir = Path(temp_dir) / "extracted"
        extract_dir.mkdir()
        with pyzipper.AESZipFile(zip_temp, "r") as zf:
            zf.setpassword(password.encode("utf-8"))
            zf.extractall(extract_dir)

        cipher_file = None
        original_name = None
        for f in extract_dir.iterdir():
            if f.suffix == ".ciper":
                cipher_file = f
                original_name = f.read_text(encoding="utf-8")
                break

        if original_name is None:
            raise FileNotFoundError(".ciper file not found in ZIP")

        decrypted_file = None
        for f in extract_dir.iterdir():
            if f.suffix != ".ciper":
                decrypted_file = f
                break

        if decrypted_file is None:
            raise FileNotFoundError("Encrypted file not found in ZIP")

        decrypted_name = original_name
        final_path = output_dir / decrypted_name
        shutil.copy(decrypted_file, final_path)

        return {
            "original_name": original_name,
            "decrypted_name": decrypted_name,
            "decrypted_path": str(final_path),
        }
