import Cookies from "js-cookie";

export async function removeAuth() {
  Cookies.remove("accessToken");
}
